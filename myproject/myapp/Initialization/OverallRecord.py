from ..models import DailyRecord, RequestForm,AttendanceCount,Employee,Branches
from django.db.models import Q, Sum
from django.shortcuts import render, redirect,get_object_or_404
from datetime import date, time, datetime, timedelta, timezone
from collections import defaultdict
from django.http import JsonResponse
import math
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string


def is_admin(user):
    return user.groups.filter(name='admingroup').exists()

def TwoDigit(input):
    result = str(input.count()).zfill(2)
    return result

@login_required(login_url='login')
def home(request):
    branches = Branches.objects.all()
    # For Late Employees
    late_condition = ["Late AM", "Late PM", "Late AM-PM"]
    current_date = date.today().strftime('%Y-%m-%d')
    current_month = datetime.now().month
    late_query = DailyRecord.objects.filter(late__in=late_condition, date=current_date)
    latecount_formatted = TwoDigit(late_query)
    total_latecount_sum_s = DailyRecord.objects.filter(date__month = current_month, late__in=late_condition).values('EmpCode_id').annotate(total_latecount_sum=Sum('latecount'))
    total_latecount_sum = sum(item['total_latecount_sum'] for item in total_latecount_sum_s)
    

    try:
        if total_latecount_sum is not None:
            total_latecount_sum = int(total_latecount_sum)
        else:
            total_latecount_sum = 0
    except:
        total_latecount_sum = 0

    # For Absent Employee
    employee_in_branch = Employee.objects.filter(BranchCode__BranchCode='EMB-MAIN').values_list('EmpCode', flat=True)
    absent_empcode = set(employee_in_branch) - set(DailyRecord.objects.filter(date=current_date).values_list('EmpCode__EmpCode', flat=True))
    absent_employee = Employee.objects.filter(EmpCode__in=absent_empcode)

    absent_condition = ["Absent AM", "Absent PM", "Absent"]
    marked_absent_employee = DailyRecord.objects.filter(date=current_date, absent__in=absent_condition).values_list('EmpCode__EmpCode', flat=True)
    marked_absent_employee = Employee.objects.filter(EmpCode__in=marked_absent_employee)

    all_absent_employee = Employee.objects.filter(
        Q(EmpCode__in=absent_empcode) | Q(EmpCode__in=marked_absent_employee)
    )

    absent_count = TwoDigit(all_absent_employee)

# Now you can use absent_empcode in your code as needed



    # For No Break Out and Break In
    employee_brin_brout = DailyRecord.objects.filter(Q(breakout__isnull= True) | Q(breakin__isnull= True),date=current_date)
    employee_brin_brout_count = TwoDigit(employee_brin_brout)

    # For Overtime Employee
    # employee_overtime = DailyRecord.objects.filter(date=current_date,approveOT = 1)
    # employee_overtime_count = TwoDigit(employee_overtime)


    running_formemo = DailyRecord.objects.filter(date__month = current_month,latecount__gt=0)
    
    unique_records = {}

    for record in running_formemo:
        if record.EmpCode not in unique_records:
            unique_records[record.EmpCode] = record

    unique_records_list = list(unique_records.values())



    user_in_admingroup = is_admin(request.user)
    return render(request, 'temp_myapp/home.html', {'user_in_admingroup': user_in_admingroup, 'latecount': latecount_formatted,
        'laterecord': late_query, 'total_latecount_sum':total_latecount_sum,  'absentemployee': all_absent_employee,
        'absentcount': absent_count, 'breakinbreakout': employee_brin_brout, 'breakinbreakoutcount': employee_brin_brout_count,
        'running_formemo': unique_records_list,'branches':branches})



def overallattendance(request):
    # Assuming you have already retrieved emp_code_from_html and current_date as shown in the previous example
    emp_code_from_html = request.POST.get('empCode')  # Use the appropriate method (POST or GET)
    current_date = date.today()

    try:
        # Query the DailyRecord model to retrieve data for the specified employee and date
        records = DailyRecord.objects.filter(EmpCode__EmpCode=emp_code_from_html, date=current_date)

        # Calculate attendance count
        attendance_count = records.count()

        # Pass the retrieved data to the template context
        context = {
            'attendanceCount': attendance_count,
            'breakinbreakout': records,
        }

        return render(request, 'temp_myapp/home.html', context)
    except DailyRecord.DoesNotExist:
        # Handle the case where no record is found for the specified employee and date
        return render(request, 'temp_myapp/home.html', {'error_message': 'No record found for the specified employee and date'})





def calculate_total_hours_worked(records):
    total_seconds_worked = 0
    break_time = 3600  # Fixed 1-hour break time in seconds

    # Define work hours
    work_start = datetime.combine(datetime.today(), time(7, 0, 0))
    break_out = datetime.combine(datetime.today(), time(12, 0, 0))
    break_in = datetime.combine(datetime.today(), time(13, 0, 0))
    work_end = datetime.combine(datetime.today(), time(16, 0, 0))

    for record in records:
        # Extract "Absent" field value from the record
        absent_status = record.absent

        # Extract time parameters from the record
        timein, timeout, breakin, breakout = record.timein, record.timeout, record.breakin, record.breakout

        # Skip records with None values in time fields
        if None in (timein, timeout, breakin, breakout):
            continue

        # Convert time objects to datetime objects with a common date
        timein_datetime = datetime.combine(datetime.today(), timein)
        timeout_datetime = datetime.combine(datetime.today(), timeout)
        breakin_datetime = datetime.combine(datetime.today(), breakin)
        breakout_datetime = datetime.combine(datetime.today(), breakout)

        timein_datetime = max(timein_datetime, work_start)
        timeout_datetime = min(timeout_datetime, work_end)

        worked_duration = min(timeout_datetime, work_end) - max(timein_datetime, work_start)
        total_work_seconds = max(0, worked_duration.total_seconds())

        if total_work_seconds > 0:
            if breakin_datetime > datetime.combine(datetime.today(), time(13, 0, 0)):
                excess_break_time = (breakin_datetime - datetime.combine(datetime.today(), time(13, 0, 0))).total_seconds()
                break_time += excess_break_time
                total_work_seconds -= break_time
            else:
                total_work_seconds -= break_time

        # Adjust worked hours based on absent status
        if 'Absent AM' in absent_status:
            # Skip hours from 7 am to 12 pm
            breakin_datetime_adjusted = max(breakin_datetime, datetime.combine(breakin_datetime.date(), time(11, 0)))
            absent_duration = min(breakout_datetime, work_end) - max(breakin_datetime_adjusted, work_start)
            total_work_seconds -= max(0, absent_duration.total_seconds())
            total_work_seconds = min(total_work_seconds, (work_end - max(breakin_datetime_adjusted, work_start)).total_seconds())
            total_work_seconds -= break_time
            
        elif 'Absent PM' in absent_status:
            # Skip hours from 1 pm to 4 pm
            absent_duration = min(breakout_datetime, work_end) - max(breakin_datetime, work_start)
            total_work_seconds -= max(0, absent_duration.total_seconds())
            break_time = 0 
          
            adjusted_start_time = datetime.combine(timein_datetime.date(), time(7, 0, 0))
            adjusted_breakout_time = min(breakout_datetime, datetime.combine(breakout_datetime.date(), time(12, 0, 0)))
            total_work_seconds += max(0, (adjusted_breakout_time - max(timein_datetime, adjusted_start_time)).total_seconds())
          
            if timein_datetime < adjusted_start_time:
                early_timein_seconds = (adjusted_start_time - timein_datetime).total_seconds()
                total_work_seconds += max(0, early_timein_seconds)

        elif 'Absent' in absent_status:
            total_work_seconds = 0

        total_seconds_worked += total_work_seconds

    total_time = timedelta(seconds=total_seconds_worked)

    total_hours = total_time.days * 24 + total_time.seconds // 3600
    total_minutes = (total_time.seconds % 3600) // 60

    return total_hours, total_minutes









# For Calculating the Undertime
def calculate_undertime_for_record(record, field_name, upper_bound_time):
    undertime_duration = timedelta()

    field_value = getattr(record, field_name)

    if field_value:
        field_datetime = datetime.combine(record.date, field_value)

        if field_datetime < datetime.combine(record.date, upper_bound_time):
            undertime_duration = max(datetime.combine(record.date, upper_bound_time) - field_datetime, timedelta())

    return undertime_duration

def CalculateUndertime(attendance_records):
    total_undertime = timedelta()
    total_undertime_count = 0

    for record in attendance_records:
        if record.timeout != time(0, 0):  # Check if timeout is not midnight
            # Convert record.timeout to string and then to timedelta for comparison
            
            undertime_duration = calculate_undertime_for_record(record, "timeout", time(16, 0, 0))

            # Check if undertime_duration is not equal to zero timedelta
            if undertime_duration != timedelta():
                total_undertime += undertime_duration
                record.totalundertime = undertime_duration
                record.save()
                undertime_count = count_undertime_intervals(undertime_duration)
                total_undertime_count += undertime_count

    return total_undertime

def count_undertime_intervals(undertime_duration):
    interval_duration = timedelta(minutes=15)
    undertime_count = math.ceil(undertime_duration.total_seconds() / interval_duration.total_seconds())

    return undertime_count
# For Calculating the Undertime










def filter_and_fetch(request):
    if request.method == 'POST':
        search_name = request.POST.get('search', '')
        branch = request.POST.get('branches', '')
        start_date_str = request.POST.get('dateStart', '')
        end_date_str = request.POST.get('endDate', '')


        query = Q()

        if search_name:
            query &= Q(Empname__icontains=search_name)
        if branch and branch != 'ALL':
            query &= Q(EmpCode_id__BranchCode_id__BranchCode=branch)
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            query &= Q(date__range=[start_date, end_date])


        filtered_records = DailyRecord.objects.filter(query)

        records_empty = not bool(filtered_records)
        



    # Use a defaultdict to accumulate hours worked and absent hours for each employee
    employee_data = defaultdict(lambda: {'TotalHoursWorked': timedelta(), 'LateCount': 0, 'TotalAbsentHours': timedelta(), 'TotalOvertime':timedelta(), 'TotalUndertime':0})



    for record in filtered_records:


        # Perform your calculations based on the DailyRecord fields
        total_hours, total_minutes = calculate_total_hours_worked([record])
        # Convert the total hours and minutes to timedelta
        total_time = timedelta(hours=total_hours, minutes=total_minutes)
        # Accumulate hours worked for each employee
        employee_data[record.Empname]['TotalHoursWorked'] += total_time
        print(f"Total hours for {record.Empname}: {employee_data[record.Empname]['TotalHoursWorked']}")
        # Accumulate late count for each employee
        employee_data[record.Empname]['LateCount'] += int(record.latecount)





        # Calculate total absent hours based on the absent marks
        if record.absent == "Absent AM":
            absent_hours = timedelta(hours=4)
        elif record.absent == "Absent PM":
            absent_hours = timedelta(hours=4)
        elif record.absent == "Absent":
            absent_hours = timedelta(hours=8)
        else:
            absent_hours = timedelta(hours=0)

        # Accumulate absent hours for each employee
        employee_data[record.Empname]['TotalAbsentHours'] += absent_hours





        # Overtime Calculation
        overtime_parts = record.totalovertime.split(':')

        if len(overtime_parts) == 3:  # Assuming format: ['1', '00', '00']
            overtime_hours, overtime_minutes, _ = map(int, overtime_parts)
        elif len(overtime_parts) == 2:  # Assuming format: ['00', '00']
            overtime_hours, overtime_minutes = map(int, overtime_parts)
        else:
            continue

        employee_data[record.Empname]['TotalOvertime'] += timedelta(hours=overtime_hours, minutes=overtime_minutes)





        # Undertime Calculation
        if record.timeout != time(0, 0):  # Check if timeout is not midnight
            undertime_duration = calculate_undertime_for_record(record, "timeout", time(16, 0, 0))
            if undertime_duration != timedelta():
                undertime_count = count_undertime_intervals(undertime_duration)

                employee_data[record.Empname]['TotalUndertime'] += undertime_count


        emp_code = record.EmpCode

    # Assuming EmpCode has fields EmpCode and BranchCode (adjust accordingly based on your actual model)
        emp_code_data = {
            'EmpCode': emp_code.EmpCode,
            'BranchCode': emp_code.BranchCode.BranchCode,
        }

        # Accumulate data for each employee
        employee_data[record.Empname].update(emp_code_data)




    # Convert the defaultdict to a list of dictionaries for rendering
    processed_employee_list = [
        {
            'BranchCode': data['BranchCode'],
            'Empname': empname,
            'TotalHoursWorked': data['TotalHoursWorked'],
            'LateCount': data['LateCount'],
            'TotalAbsentHours': data['TotalAbsentHours'],
            'TotalOvertime': data['TotalOvertime'],
            'TotalUndertime': data['TotalUndertime'],
            'EmpCode': data['EmpCode']
            
        }
        for empname, data in employee_data.items()
    ]

    # Return JSON response with an array
    return JsonResponse({'processed_employee_data': processed_employee_list,'records_empty': records_empty})




def view_employee_info(request, emp_id):
    if request.method == 'GET':
        if emp_id is not None:
            # Retrieve the employee information from the AttendanceCount model
            attendance_count_data = get_object_or_404(AttendanceCount, EmpCode=emp_id)

            # Prepare the data to be sent as JSON response
            employee_info = {
                'Vacation': attendance_count_data.Vacation,
                'Sick': attendance_count_data.Sick,
                'GracePeriod': attendance_count_data.GracePeriod,
                'last_grace_period_month': attendance_count_data.last_grace_period_month.strftime('%Y-%m-%d'),
                'last_leaves_year': attendance_count_data.last_leaves_year.strftime('%Y-%m-%d'),
            }

            return JsonResponse({'employee_info': employee_info})
        else:
            return JsonResponse({'error': 'Missing employee ID parameter'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_daily_records(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_query = request.GET.get('search')


    daily_records = DailyRecord.objects.filter(date__range=[start_date, end_date], Empname__icontains=search_query)
   
    
    # Serialize the data
    serialized_data = []
    for record in daily_records:
        serialized_data.append({
            'EmpName': record.Empname,
            'Timein': record.timein.strftime('%H:%M:%S') if record.timein else '',
            'Breakout': record.breakout.strftime('%H:%M:%S') if record.breakout else '',
            'Breakin': record.breakin.strftime('%H:%M:%S') if record.breakin else '',
            'Timeout': record.timeout.strftime('%H:%M:%S') if record.timeout else '',
            'Date':record.date,
            'LateCount':record.latecount,
            'Absent': record.absent,
            'Late':record.late,
            'Remarks': record.remarks,
            'blank':'blank'
        })

    return JsonResponse({'records': serialized_data})





def PrintPage(request):
      return render(request, 'temp_myapp/printpage.html')



def get_attendance_employee(request):
    current_month = request.current_time.month
    if request.method == 'POST':
        emp_code = request.POST.get('empCode')

        data = DailyRecord.objects.filter(EmpCode__EmpCode=emp_code, date__month = current_month).values()
        return JsonResponse(list(data), safe=False)
    else:

        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def generate_memo(request):
    current_date = datetime.today()
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
       
        try:
            record = DailyRecord.objects.get(EmpCode_id=record_id)
            num_memo = AttendanceCount.objects.get(EmpCode_id = record_id)
            total_latecount_sum = DailyRecord.objects.filter(EmpCode_id=record_id).aggregate(total_latecount_sum=Sum('latecount'))
            late_count = int(total_latecount_sum['total_latecount_sum'])
            memo_count = int(num_memo.memo)
            date = record.date
            time_in = record.timein

            # Generate memo text
            notice_type = ""
            memo_type = ""
    
            if memo_count >= 1 and memo_count <= 5:
                notice_type = "Written Warning"
                memo_type = "Written Warning"
                
            elif memo_count == 6:
                notice_type = "Notice of Suspension"
                memo_type = "3 days Suspension"
               
            elif memo_count == 7:
                notice_type = "Notice of Suspension"
                memo_type = "10-15 days Suspension"
               
            elif memo_count >= 8:
                notice_type = "Notice of Termination"
                memo_type = "Termination"
               

            memo_text = f"This memo serves as a {memo_type} concerning your repeated instance of tardiness. Our records indicate that this is your {late_count} memo regarding this issue, specifically referring to your late arrival on {date} at {time_in}.\n\n"
            memo_text += "<br><br>"
            memo_text += "Please be advised that this will be a final reminder to you to improve your punctuality record, if not totally eradicate your tardiness. This excessive number of counts will affect your performance rating and evaluation. Subsequent offense thereto will be subject to disciplinary measures.\n\n"
            memo_text += "<br><br>"
            memo_text += "As the value of discipline has always been emphasized by the company, an employee should be able to work in accordance with the schedule normal working hours. Starting work on time means ending work on time.\n\n"
            memo_text += "<br><br>"
            memo_text += "Let this memorandum serve as a warning to you. Subsequent offense related thereto will mean your suspension based on our personnel handbook and code of discipline manual. For your information and compliance.\n\n"
            memo_text += "<br><br>"
            memo_text += "<br><br>"
            memo_text += "Sincerely."

            # Render printable memo HTML
            printable_html = render(request,'temp_myapp/printmemo.html', {'memo_text': memo_text, 'notice_type':notice_type})

            # Return the rendered HTML as a response
            return HttpResponse(printable_html, content_type='text/html')
        except DailyRecord.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

