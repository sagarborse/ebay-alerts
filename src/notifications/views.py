from rest_framework import viewsets
from .models import Notification, Product
from .serializers import NotificationSerializer, ProductSerializer


# Create your views here.
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'put', 'post', 'patch', 'delete']
    queryset = Notification.objects.all()


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    http_method_names = ['get', 'put', 'post', 'patch', 'delete']
    queryset = Product.objects.all()
