#!/bin/sh
set -e

python manage.py migrate --noinput

python manage.py shell -c "
from django.contrib.auth.models import User
from employees.models import Department, LeaveType

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hrm.com', 'admin123')

for name in ['Engineering', 'Human Resources', 'Sales', 'Marketing', 'Finance', 'Operations']:
    Department.objects.get_or_create(name=name)

for name, days in [('Annual Leave', 21), ('Sick Leave', 10), ('Casual Leave', 7), ('Maternity Leave', 90), ('Paternity Leave', 15)]:
    LeaveType.objects.get_or_create(name=name, defaults={'days_allowed': days})
"

exec gunicorn hrm_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
