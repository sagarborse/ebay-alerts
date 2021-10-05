from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'alerts', views.UserProductAlertViewSet, basename="alerts")
router.register(r'products', views.UserProductViewSet, basename="products")

urlpatterns = [
    path('', include(router.urls)),
]
