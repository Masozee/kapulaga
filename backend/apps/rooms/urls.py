from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'types', views.RoomTypeViewSet)
router.register(r'', views.RoomViewSet)

urlpatterns = [
    path('', include(router.urls)),
]