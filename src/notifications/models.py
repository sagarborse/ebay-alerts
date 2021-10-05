from django.db import models

# Create your models here.
class Notification(models.Model):
    """
    Notification Setting Ckass
    """
    RECURRENCE = (
        (1, '1 minutes'),
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
    ebay_prd_id  = models.CharField(max_length=100, db_index=True)
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
        """
        :return: last checked price of the product
        """
        return self.price_set.latest('timestamp').amount

    def dict(self):
        """
        Return json serializable dict
        :return:
        """
        return {
            'id': str(self.id),
            'ebay_id': self.ebay_id,
            'title': self.title,
            'price': self.price
        }


class SendUpdate(models.Model):
    """
    Log of update sent to a user

    this is also being used to check next update
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.notification.search_phrase}: {self.timestamp.ctime()}'


class Price(models.Model):
    """
    Store product price
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.title}: {self.price}'
