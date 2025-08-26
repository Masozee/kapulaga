from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.GuestViewSet)
router.register(r'documents', views.GuestDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]