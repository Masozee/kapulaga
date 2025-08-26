from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta, date

from .models import Department, Employee, Attendance, Shift
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, EmployeeListSerializer,
    EmployeeCreateUpdateSerializer, AttendanceSerializer, AttendanceCreateUpdateSerializer,
    ShiftSerializer, AttendanceSummarySerializer, EmployeePerformanceSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing departments"""
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'manager']
    search_fields = ['name', 'description']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees in department"""
        department = self.get_object()
        employees = department.employee_set.filter(is_active=True)
        serializer = EmployeeListSerializer(employees, many=True)
        return Response({
            'department': department.name,
            'total_employees': employees.count(),
            'employees': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get department summary statistics"""
        departments = self.get_queryset()
        summary_data = []
        
        for dept in departments:
            employees = dept.employee_set.filter(is_active=True)
            summary_data.append({
                'id': dept.id,
                'name': dept.name,
                'manager': dept.manager.full_name if dept.manager else None,
                'total_employees': employees.count(),
                'budget': float(dept.budget) if dept.budget else 0,
                'total_salary_cost': float(employees.aggregate(
                    total=Sum('salary')
                )['total'] or 0),
                'average_salary': float(employees.aggregate(
                    avg=Avg('salary')
                )['avg'] or 0)
            })
        
        return Response(summary_data)

    @action(detail=True, methods=['post'])
    def set_manager(self, request, pk=None):
        """Set department manager"""
        department = self.get_object()
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if employee belongs to this department
        if employee.department != department:
            return Response({
                'error': f'Employee {employee.full_name} does not belong to {department.name} department'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        department.manager = employee
        department.save(update_fields=['manager', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'{employee.full_name} is now manager of {department.name}',
            'department': DepartmentSerializer(department).data
        })


class ShiftViewSet(viewsets.ModelViewSet):
    """ViewSet for managing work shifts"""
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-shift_date', 'start_time']

    @action(detail=True, methods=['get'])
    def shift_details(self, request, pk=None):
        """Get shift details including attendance"""
        shift = self.get_object()
        
        # Get attendance if exists
        attendance = None
        try:
            attendance = shift.attendance
            attendance_data = AttendanceSerializer(attendance).data
        except:
            attendance_data = None
        
        return Response({
            'shift': ShiftSerializer(shift).data,
            'employee': EmployeeListSerializer(shift.employee).data,
            'attendance': attendance_data,
            'hours_scheduled': shift.hours_scheduled
        })


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing employees"""
    queryset = Employee.objects.select_related('department', 'shift').filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'position', 'shift', 'employment_type', 'is_active']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'hire_date', 'salary']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeSerializer

    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        """Get employee's attendance history"""
        employee = self.get_object()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        
        attendance_records = employee.attendance_set.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        
        # Calculate summary statistics
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='PRESENT').count()
        late_days = attendance_records.filter(status='LATE').count()
        absent_days = attendance_records.filter(status='ABSENT').count()
        on_leave_days = attendance_records.filter(status='ON_LEAVE').count()
        
        return Response({
            'employee': employee.full_name,
            'period': f"{start_date} to {end_date}",
            'summary': {
                'total_days': total_days,
                'present_days': present_days,
                'late_days': late_days,
                'absent_days': absent_days,
                'on_leave_days': on_leave_days,
                'attendance_rate': round((present_days / total_days) * 100, 1) if total_days > 0 else 0,
                'punctuality_rate': round(((present_days - late_days) / total_days) * 100, 1) if total_days > 0 else 0
            },
            'records': serializer.data
        })

    @action(detail=False, methods=['get'])
    def birthday_today(self, request):
        """Get employees with birthday today"""
        from datetime import date
        today = date.today()
        
        # Find employees with birthday today (month and day match)
        employees = self.get_queryset().extra(
            where=[
                "EXTRACT(month FROM hire_date) = %s AND EXTRACT(day FROM hire_date) = %s"
            ],
            params=[today.month, today.day]
        )
        
        serializer = EmployeeListSerializer(employees, many=True)
        return Response({
            'date': today,
            'birthday_count': employees.count(),
            'employees': serializer.data
        })

    @action(detail=False, methods=['get'])
    def work_anniversaries(self, request):
        """Get employees with work anniversaries this month"""
        today = timezone.now().date()
        
        employees = self.get_queryset().extra(
            where=["EXTRACT(month FROM hire_date) = %s"],
            params=[today.month]
        ).order_by('hire_date')
        
        anniversary_data = []
        for emp in employees:
            years = (today - emp.hire_date).days // 365
            if years > 0:  # Only include employees with at least 1 year
                anniversary_data.append({
                    'employee': EmployeeListSerializer(emp).data,
                    'hire_date': emp.hire_date,
                    'years_of_service': years,
                    'anniversary_date': emp.hire_date.replace(year=today.year)
                })
        
        return Response({
            'month': today.strftime('%B %Y'),
            'total_anniversaries': len(anniversary_data),
            'anniversaries': anniversary_data
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an employee"""
        employee = self.get_object()
        reason = request.data.get('reason', 'Employment terminated')
        
        employee.is_active = False
        employee.save(update_fields=['is_active', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'{employee.full_name} has been deactivated',
            'reason': reason
        })

    @action(detail=True, methods=['post'])
    def update_salary(self, request, pk=None):
        """Update employee salary"""
        employee = self.get_object()
        new_salary = request.data.get('salary')
        reason = request.data.get('reason', 'Salary adjustment')
        
        if not new_salary:
            return Response({'error': 'salary is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_salary = float(new_salary)
            if new_salary <= 0:
                raise ValueError()
        except ValueError:
            return Response({'error': 'Invalid salary amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_salary = employee.salary
        employee.salary = new_salary
        employee.save(update_fields=['salary', 'updated_at'])
        
        return Response({
            'success': True,
            'message': f'Salary updated for {employee.full_name}',
            'old_salary': float(old_salary),
            'new_salary': new_salary,
            'reason': reason,
            'employee': EmployeeSerializer(employee).data
        })


class AttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance records"""
    queryset = Attendance.objects.select_related('shift__employee').order_by('-shift__shift_date', '-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['shift__employee', 'status', 'shift__shift_date']
    search_fields = ['shift__employee__user__first_name', 'shift__employee__user__last_name', 'shift__employee__employee_id']
    ordering = ['-shift__shift_date', 'shift__employee__user__first_name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AttendanceCreateUpdateSerializer
        return AttendanceSerializer

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Employee check-in"""
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        current_datetime = timezone.now()
        
        # Find today's shift for the employee
        today_shift = Shift.objects.filter(
            employee=employee,
            shift_date=today
        ).first()
        
        if not today_shift:
            return Response({
                'error': f'No shift scheduled for {employee.full_name} today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already checked in
        try:
            attendance = today_shift.attendance
            if attendance.clock_in:
                return Response({
                    'error': f'{employee.full_name} has already checked in today at {attendance.clock_in}'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            # Create new attendance record
            attendance = Attendance.objects.create(shift=today_shift)
        
        # Determine status based on shift start time
        scheduled_start = datetime.combine(today, today_shift.start_time)
        grace_period = timedelta(minutes=15)
        
        if current_datetime <= scheduled_start + grace_period:
            status_value = 'PRESENT'
            late_minutes = 0
        else:
            status_value = 'LATE'
            late_minutes = int((current_datetime - scheduled_start).total_seconds() / 60)
        
        # Update attendance record
        attendance.clock_in = current_datetime
        attendance.status = status_value
        attendance.late_minutes = late_minutes
        attendance.save(update_fields=['clock_in', 'status', 'late_minutes'])
        
        return Response({
            'success': True,
            'message': f'{employee.full_name} checked in successfully',
            'clock_in_time': current_datetime,
            'status': attendance.get_status_display(),
            'late_minutes': late_minutes,
            'attendance': AttendanceSerializer(attendance).data
        })

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Employee check-out"""
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        # Find today's attendance record
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({
                'error': f'{employee.full_name} has not checked in today'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance.check_out_time:
            return Response({
                'error': f'{employee.full_name} has already checked out today at {attendance.check_out_time}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.check_out_time = current_time
        attendance.save(update_fields=['check_out_time'])
        
        return Response({
            'success': True,
            'message': f'{employee.full_name} checked out successfully',
            'check_out_time': current_time,
            'hours_worked': AttendanceSerializer(attendance).get_hours_worked(attendance),
            'attendance': AttendanceSerializer(attendance).data
        })

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily attendance summary"""
        # Get date from query params, default to today
        date_param = request.query_params.get('date')
        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date()
        
        # Get attendance records for the date
        attendance_records = self.get_queryset().filter(date=target_date)
        
        # Calculate statistics
        total_employees = Employee.objects.filter(is_active=True).count()
        present = attendance_records.filter(status='PRESENT').count()
        late = attendance_records.filter(status='LATE').count()
        absent = attendance_records.filter(status='ABSENT').count()
        on_leave = attendance_records.filter(status='ON_LEAVE').count()
        
        # Employees who haven't marked attendance
        marked_attendance = attendance_records.count()
        not_marked = total_employees - marked_attendance
        
        summary = {
            'date': target_date,
            'total_employees': total_employees,
            'present': present,
            'late': late,
            'absent': absent,
            'on_leave': on_leave,
            'not_marked': not_marked,
            'attendance_rate': round(((present + late) / total_employees) * 100, 1) if total_employees > 0 else 0,
            'punctuality_rate': round((present / (present + late)) * 100, 1) if (present + late) > 0 else 0
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """Get monthly attendance report"""
        # Get month/year from query params
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if month and year:
            try:
                target_date = datetime(int(year), int(month), 1).date()
            except ValueError:
                return Response({
                    'error': 'Invalid month or year'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date().replace(day=1)
        
        # Calculate month range
        if target_date.month == 12:
            next_month = target_date.replace(year=target_date.year + 1, month=1)
        else:
            next_month = target_date.replace(month=target_date.month + 1)
        
        # Get attendance data for the month
        monthly_attendance = self.get_queryset().filter(
            date__gte=target_date,
            date__lt=next_month
        )
        
        # Calculate department-wise statistics
        departments = Department.objects.filter(is_active=True)
        dept_stats = []
        
        for dept in departments:
            dept_attendance = monthly_attendance.filter(employee__department=dept)
            total_records = dept_attendance.count()
            
            if total_records > 0:
                dept_stats.append({
                    'department': dept.name,
                    'total_records': total_records,
                    'present': dept_attendance.filter(status='PRESENT').count(),
                    'late': dept_attendance.filter(status='LATE').count(),
                    'absent': dept_attendance.filter(status='ABSENT').count(),
                    'on_leave': dept_attendance.filter(status='ON_LEAVE').count(),
                    'attendance_rate': round((dept_attendance.filter(
                        status__in=['PRESENT', 'LATE']
                    ).count() / total_records) * 100, 1)
                })
        
        return Response({
            'month': target_date.strftime('%B %Y'),
            'total_records': monthly_attendance.count(),
            'overall_stats': {
                'present': monthly_attendance.filter(status='PRESENT').count(),
                'late': monthly_attendance.filter(status='LATE').count(),
                'absent': monthly_attendance.filter(status='ABSENT').count(),
                'on_leave': monthly_attendance.filter(status='ON_LEAVE').count()
            },
            'department_stats': dept_stats
        })
