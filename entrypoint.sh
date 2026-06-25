#!/bin/sh
set -e

python manage.py migrate --noinput

python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hrm.com', 'admin123')
    print('Superuser created: admin/admin123')
"

python manage.py shell -c "
from employees.models import Department, LeaveType
depts = ['Engineering', 'Human Resources', 'Sales', 'Marketing', 'Finance', 'Operations']
for d in depts:
    Department.objects.get_or_create(name=d)

leaves = [('Annual Leave', 21), ('Sick Leave', 10), ('Casual Leave', 7), ('Maternity Leave', 90), ('Paternity Leave', 15)]
for name, days in leaves:
    LeaveType.objects.get_or_create(name=name, defaults={'days_allowed': days})
print('Seed data created')
"

exec gunicorn hrm_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
