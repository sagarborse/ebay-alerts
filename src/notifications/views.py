from rest_framework import viewsets

from .models import Notification, Product
from .serializers import NotificationSerializer, ProductSerializer

# Create your views here.
class UserProductAlertViewSet(viewsets.ModelViewSet):
    """
    Simple model viewSet to create, update and delete product alert
    """
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'put', 'post', 'patch', 'delete']
    queryset = Notification.objects.all()


class UserProductViewSet(viewsets.ModelViewSet):
    """
    Simple model viewSet to create, update and delete product alert
    """
    serializer_class = ProductSerializer
    http_method_names = ['get', 'put', 'post', 'patch', 'delete']
    queryset = Product.objects.all()
