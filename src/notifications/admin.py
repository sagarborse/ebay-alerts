from django.contrib import admin
from notifications import models

admin.site.register(models.Product)
admin.site.register(models.Amount)
admin.site.register(models.Notification)
admin.site.register(models.SendUpdate)
