from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class Employee(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('TERMINATED', 'Terminated'),
        ('RESIGNED', 'Resigned'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='ACTIVE')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = self.generate_employee_id()
        super().save(*args, **kwargs)

    def generate_employee_id(self):
        """Generate employee ID automatically"""
        prefix = 'EMP'
        count = Employee.objects.count() + 1
        return f"{prefix}{count:04d}"


class Shift(models.Model):
    SHIFT_TYPE_CHOICES = [
        ('MORNING', 'Morning Shift'),
        ('AFTERNOON', 'Afternoon Shift'),
        ('EVENING', 'Evening Shift'),
        ('NIGHT', 'Night Shift'),
        ('OVERTIME', 'Overtime'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shifts')
    shift_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES, default='MORNING')
    break_duration = models.PositiveIntegerField(default=60, help_text='Break duration in minutes')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-shift_date', 'start_time']
        unique_together = ['employee', 'shift_date', 'start_time']
        verbose_name = 'Shift'
        verbose_name_plural = 'Shifts'

    def __str__(self):
        return f"{self.employee.full_name} - {self.shift_date} ({self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')})"

    @property
    def hours_scheduled(self):
        """Calculate scheduled hours for the shift"""
        start_datetime = datetime.combine(self.shift_date, self.start_time)
        end_datetime = datetime.combine(self.shift_date, self.end_time)
        
        # Handle overnight shifts
        if self.end_time < self.start_time:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        hours = duration.total_seconds() / 3600
        
        # Subtract break duration
        break_hours = self.break_duration / 60
        return max(0, hours - break_hours)


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('LATE', 'Late'),
        ('ABSENT', 'Absent'),
        ('SICK', 'Sick Leave'),
        ('VACATION', 'Vacation'),
        ('OVERTIME', 'Overtime'),
    ]

    shift = models.OneToOneField(Shift, on_delete=models.CASCADE, related_name='attendance')
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    late_minutes = models.PositiveIntegerField(default=0)
    overtime_minutes = models.PositiveIntegerField(default=0)
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-shift__shift_date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.shift.employee.full_name} - {self.shift.shift_date} - {self.status}"

    @property
    def hours_worked(self):
        """Calculate actual hours worked"""
        if not self.clock_in or not self.clock_out:
            return 0
        
        duration = self.clock_out - self.clock_in
        hours = duration.total_seconds() / 3600
        
        # Subtract break time if recorded
        if self.break_start and self.break_end:
            break_duration = self.break_end - self.break_start
            break_hours = break_duration.total_seconds() / 3600
            hours -= break_hours
        
        return max(0, hours)

    def is_late(self):
        """Check if employee was late"""
        if not self.clock_in:
            return False
        
        scheduled_start = datetime.combine(
            self.shift.shift_date, 
            self.shift.start_time
        )
        return self.clock_in > scheduled_start

    def is_early_departure(self):
        """Check if employee left early"""
        if not self.clock_out:
            return False
        
        scheduled_end = datetime.combine(
            self.shift.shift_date, 
            self.shift.end_time
        )
        
        # Handle overnight shifts
        if self.shift.end_time < self.shift.start_time:
            scheduled_end += timedelta(days=1)
        
        return self.clock_out < scheduled_end

    def save(self, *args, **kwargs):
        # Calculate late minutes if clocked in late
        if self.clock_in and self.is_late():
            scheduled_start = datetime.combine(
                self.shift.shift_date, 
                self.shift.start_time
            )
            late_duration = self.clock_in - scheduled_start
            self.late_minutes = int(late_duration.total_seconds() / 60)
        
        super().save(*args, **kwargs)
