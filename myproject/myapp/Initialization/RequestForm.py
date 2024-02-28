
from django.shortcuts import render, get_object_or_404
from ..models import DailyRecord, Employee, RequestForm, AttendanceCount,temporray
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta, time
from django.db.models import Q
from django.db.models import F
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

def parse_time(time_str):
    formats_to_try = ['%M:%S', '%H:%M:%S']
    for fmt in formats_to_try:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            pass
    # If none of the formats worked, raise an error or return a default value
    raise ValueError("Unable to parse time string with any of the given formats")

def count_lateness_intervals(lateness_duration):
    total_minutes = lateness_duration.total_seconds() // 60
    
    if total_minutes % 15 == 0:
        lateness_count = total_minutes // 15
    else:
        lateness_count = total_minutes // 15 + 1
    
    return int(lateness_count)


def create_request(request_type, DeductRange, EmpCode_id, is_approved, remarks, attendace_count, requestdate):
    default_date = "2023-12-20"
    static_begin_time_off = datetime.strptime(f"{default_date}T07:00:00", "%Y-%m-%dT%H:%M:%S")
    static_conclude_time_off = datetime.strptime(f"{default_date}T16:00:00", "%Y-%m-%dT%H:%M:%S")
    

    dynamic_date = datetime.strptime(requestdate, "%Y-%m-%d").strftime("%Y-%m-%d")
    static_begin_time_off = static_begin_time_off.replace(year=int(dynamic_date[:4]), month=int(dynamic_date[5:7]), day=int(dynamic_date[8:10]))
    static_conclude_time_off = static_conclude_time_off.replace(year=int(dynamic_date[:4]), month=int(dynamic_date[5:7]), day=int(dynamic_date[8:10]))
    employee = Employee.objects.get(EmpCode=EmpCode_id)
    empname = f"{employee.Firstname} {employee.Lastname}"
    possible_absent_status = ["Absent", "Absent AM", "Absent PM"]
    if DeductRange == "AM":
        fixed_time = time(7,0,0)
        static_conclude_time_off = datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S")
        daily_record_am = DailyRecord.objects.filter(EmpCode_id=EmpCode_id, date=dynamic_date)
    
        if daily_record_am.exists(): 
            time_record = daily_record_am.first().timein
            breakout_record = daily_record_am.first().breakout
            late_status = daily_record_am.first().late
            absent_status = daily_record_am.first().absent
            total_lateness = daily_record_am.first().totallateness
            record_date = daily_record_am.first().date
            total_lateness_time = parse_time(total_lateness)
            fixed_datetime = datetime.combine(record_date, fixed_time)
            time_record_datetime = datetime.combine(record_date, time_record)
            lateness_datetime = datetime.combine(record_date, total_lateness_time)
            if time_record > fixed_time:
                if absent_status in possible_absent_status:
                    am_lateness_count = int(0)
                    daily_record_am.update(
                        remarks = f'Original attendance for leave cancelation: timein {time_record}, breakout {breakout_record}, lateness {total_lateness}, latecount {am_lateness_count}, latestatus {late_status}, absentstatus {absent_status}',
                        timein = static_begin_time_off.time(),
                        breakout = datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S").time(),
                        late = "None",
                        absent = "None"
                    )
                else:
                    lateness_duration = time_record_datetime - fixed_datetime
                    am_lateness_count = count_lateness_intervals(lateness_duration)
                    am_lateness_deduct = lateness_datetime - lateness_duration
                    daily_record_am.update(
                        remarks = f'Original attendance for leave cancelation: timein {time_record}, breakout {breakout_record}, lateness {total_lateness}, latecount {am_lateness_count}, latestatus {late_status}, absentstatus {absent_status}',
                        timein=static_begin_time_off.time(),
                        breakout=datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S").time(),
                        late = "Late PM" if late_status == "Late AM-PM" else "None",
                        totallateness = am_lateness_deduct.time(),
                        latecount = max(0,int(daily_record_am.first().latecount) - am_lateness_count),
                        absent = "None"
                    )
            elif absent_status in possible_absent_status:
                am_lateness_count = int(0)
                daily_record_am.update(
                    remarks = f'Original attendance for leave cancelation: timein {time_record}, breakout {breakout_record}, lateness {total_lateness}, latecount {am_lateness_count}, latestatus {late_status}, absentstatus {absent_status}',
                    timein = static_begin_time_off.time(),
                    breakout = datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S").time(),
                    late = "None",
                    absent = "None"
                )

        elif not daily_record_am.exists():
            daily_record_am.create(
                EmpCode_id=EmpCode_id,
                date=dynamic_date,
                Empname =  empname,
                late = "None",
                totallateness = "00:00",
                latecount = "0",
                absent = "None",
                timein = static_begin_time_off.time(),
                breakout = datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S"),
                remarks = f"Apply for {request_type} Leave {DeductRange}"
            )
            temporray.objects.create(
                employee_number = EmpCode_id,
                Empname = empname,
                date = dynamic_date,
                timein_timestamps = static_begin_time_off,
                timein_names = EmpCode_id,
                breakout_timestamps = datetime.strptime(f"{default_date}T12:00:00", "%Y-%m-%dT%H:%M:%S"),
                breakout_names = EmpCode_id

            )
             
             

            
    elif DeductRange == "PM":
        breakin_fixed_time = time(13,0,0)
        static_begin_time_off = datetime.strptime(f"{dynamic_date}T13:00:00", "%Y-%m-%dT%H:%M:%S")
        daily_record_pm = DailyRecord.objects.filter(EmpCode_id=EmpCode_id, date=dynamic_date)
        if daily_record_pm.exists():
            breakin_record = daily_record_pm.first().breakin
            timeout_record = daily_record_pm.first().timeout
            breakin_late_status = daily_record_pm.first().late
            breakin_absent_status = daily_record_pm.first().absent
            breakin_total_lateness = daily_record_pm.first().totallateness
            breakin_record_date = daily_record_pm.first().date
            breakin_totallatenes_time = parse_time(breakin_total_lateness)
            breakin_datetime = datetime.combine(breakin_record_date, breakin_fixed_time)
            if breakin_record:
                breakin_time_record_datetime = datetime.combine(breakin_record_date, breakin_record)
                breakin_latenes_datetime = datetime.combine(breakin_record_date, breakin_totallatenes_time)
                if breakin_record > breakin_fixed_time:
                    breakin_lateness_duration = breakin_time_record_datetime - breakin_datetime
                    pm_lateness_count = count_lateness_intervals(breakin_lateness_duration)
                    pm_lateness_deduct = breakin_latenes_datetime - breakin_lateness_duration
                    daily_record_pm.update(
                        remarks = f'Original attendance for leave cancelation: breakin {breakin_record}, timeout {timeout_record}, lateness {breakin_total_lateness}, latecount {pm_lateness_count}, latestatus {breakin_late_status}, absentstatus {breakin_absent_status}',
                        breakin=datetime.strptime(f"{dynamic_date}T12:59:00", "%Y-%m-%dT%H:%M:%S").time(),
                        timeout=datetime.strptime(f"{dynamic_date}T16:00:00", "%Y-%m-%dT%H:%M:%S").time(),
                        late = "Late AM" if breakin_late_status == "Late AM-PM" else "None",
                        totallateness = pm_lateness_deduct.time(),
                        latecount = max(0,int(daily_record_pm.first().latecount)- pm_lateness_count),
                        absent = "None"
                    )
            else:
                daily_record_pm.update(
                breakin=static_begin_time_off.time(),
                timeout=datetime.strptime(f"{dynamic_date}T16:00:00", "%Y-%m-%dT%H:%M:%S").time(),
                remarks = f'Original attendance for leave cancelation: breakin {breakin_record}, timeout {timeout_record}',
            )

    else:
        daily_record, created = DailyRecord.objects.get_or_create(
            EmpCode_id=EmpCode_id,
            date=dynamic_date,
            Empname =  empname,
            late = "None",
            totallateness = "00:00",
            latecount = "0",
            absent = "None",
            remarks = f"Apply for {request_type} Leave",
            defaults={
                'timein': static_begin_time_off.time(),
                'breakout': datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S").time(),
                'breakin': datetime.strptime(f"{dynamic_date}T12:59:00", "%Y-%m-%dT%H:%M:%S").time(),
                'timeout': datetime.strptime(f"{dynamic_date}T16:00:00", "%Y-%m-%dT%H:%M:%S").time(),
            }
            
        )
        if not created:
            # If the record already exists, update the time fields to default values
            daily_record.timein = static_begin_time_off.time()
            daily_record.breakout = datetime.strptime(f"{dynamic_date}T12:00:00", "%Y-%m-%dT%H:%M:%S").time()
            daily_record.breakin = datetime.strptime(f"{dynamic_date}T12:59:00", "%Y-%m-%dT%H:%M:%S").time()
            daily_record.timeout = datetime.strptime(f"{dynamic_date}T16:00:00", "%Y-%m-%dT%H:%M:%S").time()
            
            daily_record.save()

    RequestForm.objects.create(
        EmpCode_id=EmpCode_id,
        SelectRequest=request_type,
        BeginTimeOff=static_begin_time_off,
        Range=DeductRange,
        ConcludeTimeOff=static_conclude_time_off,
        isApproved=is_approved,
        Remarks=remarks,
        date =  requestdate
    )

    deduction_value = 0.5 if DeductRange in ["AM", "PM"] else 1.0

    if request_type == "Vacation":
        attendace_count.Vacation -= deduction_value
    elif request_type == "Sick":
        attendace_count.Sick -= deduction_value

def RequestForms(request):
        query = request.POST.get("searchquery", "")

        if query:
                form_list = RequestForm.objects.filter(  Q(BeginTimeOff__icontains=query) | Q(ConcludeTimeOff__icontains=query) | Q(EmpCode__Lastname__icontains=query))
        else:
                form_list = RequestForm.objects.all().order_by('created_at')
                
        page = request.GET.get('page', 1)
        paginator = Paginator(form_list, 7)  

        try:
                form_list = paginator.page(page)
        except PageNotAnInteger:
                form_list = paginator.page(1)
        except EmptyPage:
                form_list = paginator.page(paginator.num_pages)

        possible_deductrange = ['AM', 'PM', 'Whole']
        possible_request = ['Locator', 'Trip Ticket', 'Sick', 'Vacation', 'Paternity']
        context = {
                'possible_request':possible_request,
                'possible_deductrange':possible_deductrange,
                'form_list': form_list,

        }
            
        if request.method == "POST":
                if "add" in request.POST:
                        EmpCode_id = request.POST.get('Empcode')
                        request_type = request.POST.get('Request')
                        out_time_date = request.POST.get('OutTimeDate')
                        in_time_date = request.POST.get('InTimeDate')
                        is_approved = request.POST.get('isapproved') == "true"
                        DeductRange = request.POST.get('DeductRange')
                        remarks = request.POST.get('remarks')
                        requestdate = request.POST.get('requestdate')

                        attendace_count = AttendanceCount.objects.get(EmpCode_id=EmpCode_id)

                        if out_time_date and in_time_date:
                                begin_time_off = datetime.strptime(in_time_date, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
                                conclude_time_off = datetime.strptime(out_time_date, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")

                                RequestForm.objects.create(
                                EmpCode_id=EmpCode_id,
                                SelectRequest=request_type,
                                BeginTimeOff=begin_time_off,
                                Range = "N/A",
                                ConcludeTimeOff=conclude_time_off,
                                isApproved=is_approved,
                                Remarks=remarks,
                                        )
                                
                                messages.success(request, 'Request Submmited Successfully.', extra_tags='added')

                        elif not(out_time_date and in_time_date) and request_type in ["Vacation", "Sick", "Paternity"] and (attendace_count.Vacation > 0 or attendace_count.Sick > 0):
                                try:
                                    create_request(request_type, DeductRange, EmpCode_id, is_approved, remarks,attendace_count,requestdate) 
                                    attendace_count.save()
                                
                                    messages.success(request, 'Request Submmited Successfully.', extra_tags='added')

                                    

                                except AttendanceCount.DoesNotExist:
                                        print("AttendanceCount not found for the specified EmpCode")
                        else:
                                messages.success(request, "Employee has not been granted any leaves yet.", extra_tags='NoLeave')

                        return HttpResponseRedirect(request.path)
                
                elif "delete" in request.POST:
                        FormID = request.POST.get("FormID")
                        EmpCode_id = request.POST.get('EmpCode')
                        Range = request.POST.get('Range')
                        RequestType = request.POST.get('RequestType')
                        deleted_request = RequestForm.objects.get(FormID=FormID)
                        deleted_request.delete()
                        attendace_count = AttendanceCount.objects.get(EmpCode_id=EmpCode_id)
                        att_remarks = DailyRecord.objects.filter(EmpCode_id= EmpCode_id)



                        deduction_value = 0.5 if Range in ["AM", "PM"] else 1.0

                        if RequestType == "Vacation":
                            attendace_count.Vacation += deduction_value
                        elif RequestType == "Sick":
                            attendace_count.Sick += deduction_value
                        if deduction_value == 1.0:
                            
                            deleted_date = deleted_request.date.strftime("%Y-%m-%d")
                            
                            try:
                                record_to_delete = DailyRecord.objects.get(EmpCode_id=EmpCode_id, date=deleted_date)
                                record_to_delete.delete()
                            except DailyRecord.DoesNotExist:
                                pass

                        # elif deduction_value == 0.5 and Range in ["AM", "PM"] and att_remarks.remarks == "Apply for Sick Leave AM":
                        #     try:
                        #         record_to_delete = DailyRecord.objects.get(EmpCode_id=EmpCode_id, date=deleted_date)
                        #         record_to_delete.delete()
                        #     except DailyRecord.DoesNotExist:
                        #         pass
                        
                        

                        elif deduction_value == 0.5 and Range == "AM":
                            deleted_date = deleted_request.date.strftime("%Y-%m-%d")
                            get_records = DailyRecord.objects.filter(EmpCode_id=EmpCode_id, date=deleted_date)
                            if get_records.exists():
                                first_record = get_records.first()
                                am_current_late_count = first_record.latecount
                                get_remarks = first_record.remarks

                                pattern = r"timein\s*(\d{2}:\d{2}:\d{2}),\s*breakout\s*(\d{2}:\d{2}:\d{2}),\s*lateness\s*(\d{2}:\d{2}),\s*latecount\s*(\d{1}),\s*latestatus\s*([A-Za-z -]+),\s*absentstatus\s*([A-Za-z -]+)"
                                
                                match = re.search(pattern, get_remarks)
                                
                                if match:
                                    timein_value = match.group(1)
                                    breakout_value = match.group(2)
                                    lateness_value = match.group(3)
                                    latecount_value = match.group(4)
                                    latestatus_value = match.group(5)
                                    absentstatus_value = match.group(6)


                                    try:
                                        record_to_update = DailyRecord.objects.get(EmpCode_id=EmpCode_id, date=deleted_date)
                                        record_to_update.breakout = breakout_value
                                        record_to_update.timein = timein_value
                                        record_to_update.totallateness = lateness_value
                                        record_to_update.latecount = int(am_current_late_count) + int(latecount_value)
                                        record_to_update.late = latestatus_value
                                        record_to_update.absent = absentstatus_value
                                        record_to_update.save()
                                    except DailyRecord.DoesNotExist:
                                        pass
                                else: 
                                    print('No Match')
                            else:
                                print('No records found in DailyRecord')
                            
                                     
                        elif deduction_value == 0.5 and Range == "PM":
                            deleted_date = deleted_request.date.strftime("%Y-%m-%d")
                            get_pm_records = DailyRecord.objects.filter(EmpCode_id=EmpCode_id, date=deleted_date)
                            get_pm_remarks = get_pm_records.first().remarks
                            
                            print("PM Remarks:", get_pm_remarks)  # Debugging statement
                            
                            pm_pattern = r"breakin\s*(\d{2}:\d{2}:\d{2}),\s*timeout\s*(\d{2}:\d{2}:\d{2}),\s*lateness\s*(\d{2}:\d{2}(?::\d{2})?),\s*latecount\s*(\d{1}),\s*latestatus\s*([A-Za-z -]+),\s*absentstatus\s*([A-Za-z -]+)"

                            print("PM Pattern:", pm_pattern)  # Debugging statement
                            
                            match = re.search(pm_pattern, get_pm_remarks)
                            print("PM Match:", match)  # Debugging statement
                            
                            if match:
                                breakin_value = match.group(1)
                                timeout_value = match.group(2)
                                pm_lateness_value = match.group(3)
                                pm_latecount_value = match.group(4)
                                pm_latestatus_value = match.group(5)
                                pm_absentstatus_value = match.group(6)
                                try:
                                    record_to_update = DailyRecord.objects.get(EmpCode_id=EmpCode_id, date=deleted_date)
                                    record_to_update.breakin = breakin_value
                                    record_to_update.timeout = timeout_value
                                    record_to_update.totallateness = pm_lateness_value
                                    record_to_update.latecount = pm_latecount_value
                                    record_to_update.late = pm_latestatus_value
                                    record_to_update.absent = pm_absentstatus_value
                                    record_to_update.save()
                                except DailyRecord.DoesNotExist:
                                    pass
                            else:
                                print('No Match for PM')

        
                        attendace_count.save()
                        messages.success(request, 'Data deleted successfully!',extra_tags='delete')
                        return redirect('RequestForms')
                
   
        

        elif "search" in request.POST: 
            query = request.POST.get("searchquery", "")
            if query:
                attendance_records = attendance_records.filter(Q(isApproved__icontains=query) | Q(created_at__icontains=query))
            else:
                attendance_records = RequestForm.objects.all().order_by('created_at')
            
            paginator = Paginator(attendance_records, 5)  # Reset paginator
            page = request.GET.get('page', 1)

            try:
                attendance_records = paginator.page(page)
            except PageNotAnInteger:
                attendance_records = paginator.page(1)
            except EmptyPage:
                attendance_records = paginator.page(paginator.num_pages)
            
    
            return render(request, 'temp_myapp/EmployeeDetails.html', {'attendance_records': attendance_records, 'query': query,}, context)   
        
      
     
        return render(request, 'temp_myapp/RequestForm.html', context)



def search_view(request):
    try:
        query = request.GET.get('query', '')
        results = Employee.objects.filter(EmpCode__icontains=query)
        data = [{'EmpCode': obj.EmpCode, 'empcode': obj.EmpCode} for obj in results]
        return JsonResponse({'data': data})
    except Exception as e:
        print(f'Error in search_view: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)
