from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Employee, Department, LeaveRequest, Attendance, Announcement, LeaveType
from .forms import EmployeeForm, DepartmentForm, LeaveRequestForm, AttendanceForm, LeaveReviewForm


@login_required
def dashboard(request):
    total_employees = Employee.objects.filter(status='active').count()
    total_departments = Department.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    today = timezone.now().date()
    present_today = Attendance.objects.filter(date=today, status='present').count()
    recent_employees = Employee.objects.order_by('-created_at')[:5]
    recent_leaves = LeaveRequest.objects.order_by('-applied_on')[:5]
    announcements = Announcement.objects.filter(is_active=True)[:3]
    dept_stats = Department.objects.annotate(emp_count=Count('employee')).order_by('-emp_count')[:5]

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'pending_leaves': pending_leaves,
        'present_today': present_today,
        'recent_employees': recent_employees,
        'recent_leaves': recent_leaves,
        'announcements': announcements,
        'dept_stats': dept_stats,
    }
    return render(request, 'employees/dashboard.html', context)


@login_required
def employee_list(request):
    query = request.GET.get('q', '')
    dept = request.GET.get('dept', '')
    status = request.GET.get('status', '')

    employees = Employee.objects.select_related('department')
    if query:
        employees = employees.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(designation__icontains=query)
        )
    if dept:
        employees = employees.filter(department_id=dept)
    if status:
        employees = employees.filter(status=status)

    departments = Department.objects.all()
    context = {
        'employees': employees,
        'departments': departments,
        'query': query,
        'selected_dept': dept,
        'selected_status': status,
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    leave_requests = employee.leave_requests.order_by('-applied_on')[:5]
    attendance_records = employee.attendances.order_by('-date')[:10]
    context = {
        'employee': employee,
        'leave_requests': leave_requests,
        'attendance_records': attendance_records,
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully.')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Add Employee'})


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return redirect('employee_detail', pk=pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Edit Employee', 'employee': employee})


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully.')
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})


@login_required
def department_list(request):
    departments = Department.objects.annotate(emp_count=Count('employee'))
    return render(request, 'employees/department_list.html', {'departments': departments})


@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Add Department'})


@login_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Edit Department'})


@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted.')
        return redirect('department_list')
    return render(request, 'employees/department_confirm_delete.html', {'department': department})


@login_required
def leave_list(request):
    status_filter = request.GET.get('status', '')
    leaves = LeaveRequest.objects.select_related('employee', 'leave_type')
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    return render(request, 'employees/leave_list.html', {'leaves': leaves, 'status_filter': status_filter})


@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            try:
                leave.employee = request.user.employee
            except Exception:
                employees = Employee.objects.all()
                if employees.exists():
                    leave.employee = employees.first()
                else:
                    messages.error(request, 'No employee profile found.')
                    return redirect('leave_list')
            leave.save()
            messages.success(request, 'Leave request submitted.')
            return redirect('leave_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'employees/leave_form.html', {'form': form, 'title': 'Apply for Leave'})


@login_required
def leave_review(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        form = LeaveReviewForm(request.POST, instance=leave)
        if form.is_valid():
            reviewed = form.save(commit=False)
            reviewed.reviewed_by = request.user
            reviewed.reviewed_on = timezone.now()
            reviewed.save()
            messages.success(request, 'Leave request reviewed.')
            return redirect('leave_list')
    else:
        form = LeaveReviewForm(instance=leave)
    return render(request, 'employees/leave_review.html', {'form': form, 'leave': leave})


@login_required
def attendance_list(request):
    date_filter = request.GET.get('date', '')
    emp_filter = request.GET.get('employee', '')
    records = Attendance.objects.select_related('employee')
    if date_filter:
        records = records.filter(date=date_filter)
    if emp_filter:
        records = records.filter(employee_id=emp_filter)
    employees = Employee.objects.filter(status='active')
    context = {
        'records': records[:100],
        'employees': employees,
        'date_filter': date_filter,
        'emp_filter': emp_filter,
    }
    return render(request, 'employees/attendance_list.html', context)


@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance recorded.')
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'employees/attendance_form.html', {'form': form, 'title': 'Record Attendance'})
