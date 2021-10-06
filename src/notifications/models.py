from django.db import models


# Create your models here.
class Notification(models.Model):
    RECURRENCE = (
        (1, '1 minutes'), # Added for testing
        (2, '2 minutes'),
        (10, '10 minutes'),
        (30, '30 minutes')
    )

    email = models.EmailField()
    search_text = models.CharField(max_length=225, db_index=True)
    frequency = models.IntegerField(choices=RECURRENCE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('email', 'frequency')

    def __str__(self):
        return "{} {}".format(self.frequency, self.email)


class Product(models.Model):
    ebay_prd_id = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=225)
    location = models.TextField()
    img_url = models.URLField()
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('notification', 'ebay_prd_id')

    def __str__(self):
        return "Product : {}".format(self.title)

    @property
    def amount(self):
        return self.amount_set.latest('timestamp').amount

    def dict(self):
        return {
            'id': str(self.id),
            'ebay_prd_id': self.ebay_prd_id,
            'title': self.title,
            'amount': self.amount
        }


class SendUpdate(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.notification.search_text}: {self.timestamp.ctime()}'


class Amount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.title}: {self.amount}'
