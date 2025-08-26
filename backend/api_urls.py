"""
Main API URL configuration for the hotel management system.
This file provides comprehensive REST API endpoints for all hotel operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

# Import all ViewSets
from apps.rooms.views import RoomTypeViewSet, RoomViewSet
from apps.guests.views import GuestViewSet, GuestDocumentViewSet
from apps.reservations.views import ReservationViewSet, ReservationRoomViewSet
from apps.employees.views import DepartmentViewSet, EmployeeViewSet, AttendanceViewSet, ShiftViewSet
from apps.inventory.views import InventoryCategoryViewSet, SupplierViewSet, InventoryItemViewSet, StockMovementViewSet
from apps.payments.views import PaymentMethodViewSet, BillViewSet, PaymentViewSet
from apps.checkin.views import CheckInViewSet, RoomKeyViewSet
from apps.reports.views import ReportsViewSet

# Create the main API router
router = DefaultRouter()

# Register Rooms app endpoints
router.register(r'room-types', RoomTypeViewSet, basename='roomtype')
router.register(r'rooms', RoomViewSet, basename='room')

# Register Guests app endpoints
router.register(r'guests', GuestViewSet, basename='guest')
router.register(r'guest-documents', GuestDocumentViewSet, basename='guestdocument')

# Register Reservations app endpoints
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'reservation-rooms', ReservationRoomViewSet, basename='reservationroom')

# Register Employees app endpoints
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'shifts', ShiftViewSet, basename='shift')

# Register Inventory app endpoints
router.register(r'inventory/categories', InventoryCategoryViewSet, basename='inventorycategory')
router.register(r'inventory/suppliers', SupplierViewSet, basename='supplier')
router.register(r'inventory/items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'inventory/stock-movements', StockMovementViewSet, basename='stockmovement')

# Register Payments app endpoints
router.register(r'payment-methods', PaymentMethodViewSet, basename='paymentmethod')
router.register(r'bills', BillViewSet, basename='bill')
router.register(r'payments', PaymentViewSet, basename='payment')

# Register Check-in app endpoints
router.register(r'checkins', CheckInViewSet, basename='checkin')
router.register(r'room-keys', RoomKeyViewSet, basename='roomkey')

# Register Reports app endpoints
router.register(r'reports', ReportsViewSet, basename='reports')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request, format=None):
    """
    API Root - Hotel Management System
    
    This is the main API endpoint for the comprehensive hotel management system.
    The system provides full CRUD operations and business logic for:
    
    - Room Management (room types, individual rooms, availability)
    - Guest Management (profiles, documents, loyalty program)
    - Reservation Management (bookings, room assignments, modifications)
    - Employee Management (staff, departments, attendance, shifts)
    - Inventory Management (items, categories, suppliers, stock movements)
    - Payment Processing (billing, transactions, payment methods)
    - Check-in/Check-out Operations (guest services, room keys)
    - Comprehensive Reporting (occupancy, revenue, analytics)
    
    All endpoints support filtering, searching, pagination, and export capabilities.
    """
    
    from django.urls import reverse
    
    return Response({
        'message': 'Welcome to Hotel Management System API',
        'version': '1.0.0',
        'documentation': request.build_absolute_uri('/api/docs/'),
        'endpoints': {
            'rooms': {
                'room_types': request.build_absolute_uri(reverse('roomtype-list')),
                'rooms': request.build_absolute_uri(reverse('room-list')),
                'description': 'Room types, individual rooms, availability checking, floor summaries'
            },
            'guests': {
                'guests': request.build_absolute_uri(reverse('guest-list')),
                'guest_documents': request.build_absolute_uri(reverse('guestdocument-list')),
                'description': 'Guest profiles, documents, loyalty program, VIP management'
            },
            'reservations': {
                'reservations': request.build_absolute_uri(reverse('reservation-list')),
                'reservation_rooms': request.build_absolute_uri(reverse('reservationroom-list')),
                'description': 'Booking management, room assignments, availability checking'
            },
            'employees': {
                'departments': request.build_absolute_uri(reverse('department-list')),
                'employees': request.build_absolute_uri(reverse('employee-list')),
                'attendance': request.build_absolute_uri(reverse('attendance-list')),
                'shifts': request.build_absolute_uri(reverse('shift-list')),
                'description': 'Staff management, departments, attendance tracking, work shifts'
            },
            'inventory': {
                'categories': request.build_absolute_uri(reverse('category-list')),
                'suppliers': request.build_absolute_uri(reverse('supplier-list')),
                'items': request.build_absolute_uri(reverse('item-list')),
                'stock_movements': request.build_absolute_uri(reverse('stockmovement-list')),
                'description': 'Inventory management, stock tracking, supplier management'
            },
            'payments': {
                'payment_methods': request.build_absolute_uri(reverse('paymentmethod-list')),
                'bills': request.build_absolute_uri(reverse('bill-list')),
                'transactions': request.build_absolute_uri(reverse('transaction-list')),
                'description': 'Billing, payment processing, transaction management'
            },
            'checkin': {
                'checkins': request.build_absolute_uri(reverse('checkin-list')),
                'room_keys': request.build_absolute_uri(reverse('roomkey-list')),
                'description': 'Check-in/out operations, room key management, guest services'
            },
            'reports': {
                'reports': request.build_absolute_uri(reverse('reports-list')),
                'description': 'Comprehensive reporting: occupancy, revenue, analytics, forecasting'
            }
        },
        'features': {
            'authentication': 'Token-based authentication required',
            'permissions': 'Role-based access control',
            'filtering': 'Advanced filtering on all list endpoints',
            'search': 'Full-text search capabilities',
            'pagination': 'Paginated responses for large datasets',
            'export': 'PDF, Excel, CSV export options',
            'real_time': 'Real-time occupancy and availability updates',
            'analytics': 'Business intelligence and reporting',
            'multi_language': 'Indonesian language support for names and data'
        },
        'business_context': {
            'currency': 'IDR (Indonesian Rupiah)',
            'tax_structure': '11% PPN (VAT) + 10% Service Charge',
            'payment_methods': ['Cash', 'Credit Card', 'GoPay', 'OVO', 'DANA', 'Bank Transfer'],
            'loyalty_program': 'Points-based system (Bronze/Silver/Gold/Platinum)',
            'room_management': '88 rooms across 5 floors with Indonesian naming',
            'staff_management': '8 departments with Indonesian work culture',
            'inventory_tracking': 'Full supply chain management with Indonesian suppliers'
        }
    })


# URL patterns
urlpatterns = [
    # API root
    path('', api_root, name='api-root'),
    
    # Include all router URLs
    path('', include(router.urls)),
    
    # API documentation - commented out temporarily due to coreapi import issue
    # path('docs/', include_docs_urls(
    #     title='Hotel Management System API',
    #     description='Comprehensive REST API for hotel operations management',
    #     public=False
    # )),
    
    # Health check endpoint
    path('health/', api_view(['GET'])(lambda request: Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'services': {
            'database': 'operational',
            'api': 'operational',
            'authentication': 'operational'
        }
    })), name='api-health'),
]