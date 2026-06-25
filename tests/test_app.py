from django.test import TestCase, Client
from django.contrib.auth.models import User
from employees.models import Department, Employee, LeaveType, LeaveRequest
import datetime


class DepartmentModelTest(TestCase):
    def test_create_department(self):
        dept = Department.objects.create(name='Engineering', description='Tech team')
        self.assertEqual(dept.name, 'Engineering')
        self.assertEqual(str(dept), 'Engineering')

    def test_department_ordering(self):
        Department.objects.create(name='Zebra')
        Department.objects.create(name='Apple')
        depts = list(Department.objects.values_list('name', flat=True))
        self.assertEqual(depts, sorted(depts))


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='HR')

    def test_create_employee(self):
        emp = Employee.objects.create(
            employee_id='EMP001',
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            date_joined=datetime.date.today(),
            department=self.dept,
        )
        self.assertEqual(emp.get_full_name(), 'John Doe')
        self.assertEqual(emp.status, 'active')

    def test_employee_str(self):
        emp = Employee.objects.create(
            employee_id='EMP002', first_name='Jane', last_name='Smith',
            email='jane@test.com', date_joined=datetime.date.today(),
        )
        self.assertIn('EMP002', str(emp))


class LeaveModelTest(TestCase):
    def setUp(self):
        self.leave_type = LeaveType.objects.create(name='Annual Leave', days_allowed=21)
        self.emp = Employee.objects.create(
            employee_id='EMP003', first_name='Bob', last_name='Jones',
            email='bob@test.com', date_joined=datetime.date.today(),
        )

    def test_leave_total_days(self):
        leave = LeaveRequest.objects.create(
            employee=self.emp,
            leave_type=self.leave_type,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 5),
            reason='Vacation',
        )
        self.assertEqual(leave.total_days(), 5)

    def test_leave_default_status(self):
        leave = LeaveRequest.objects.create(
            employee=self.emp, leave_type=self.leave_type,
            start_date=datetime.date.today(), end_date=datetime.date.today(),
            reason='Test',
        )
        self.assertEqual(leave.status, 'pending')


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('testadmin', 'test@test.com', 'testpass123')

    def test_login_page_loads(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')

    def test_dashboard_with_login(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_employee_list_with_login(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get('/employees/')
        self.assertEqual(response.status_code, 200)

    def test_department_list_with_login(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get('/departments/')
        self.assertEqual(response.status_code, 200)
