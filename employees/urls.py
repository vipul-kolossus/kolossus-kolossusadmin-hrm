from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/apply/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/review/', views.leave_review, name='leave_review'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_create, name='attendance_create'),
]
