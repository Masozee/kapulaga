"""
URL configuration for kapulaga project.

This is the main URL configuration for the Hotel Management System.
It provides comprehensive REST API endpoints and Django admin interface.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone

def api_info(request):
    """Basic API information endpoint"""
    return JsonResponse({
        'name': 'Kapulaga Hotel Management System',
        'version': '1.0.0',
        'description': 'Comprehensive hotel management system with Indonesian localization',
        'api_endpoint': '/api/',
        'admin_endpoint': '/admin/',
        'timestamp': timezone.now(),
        'features': [
            'Room Management',
            'Guest Management', 
            'Reservations',
            'Employee Management',
            'Inventory Control',
            'Payment Processing',
            'Check-in/Check-out',
            'Comprehensive Reporting'
        ]
    })

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Main API endpoints
    path('api/', include('api_urls')),
    
    # Root endpoint with basic info
    path('', api_info, name='root'),
]
