from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'notify', views.NotificationViewSet, basename="notifications")
router.register(r'products', views.ProductViewSet, basename="products")

urlpatterns = [
    path('', include(router.urls)),
]
