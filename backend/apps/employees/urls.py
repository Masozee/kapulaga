from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'', views.EmployeeViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'shifts', views.ShiftViewSet)

urlpatterns = [
    path('', include(router.urls)),
]