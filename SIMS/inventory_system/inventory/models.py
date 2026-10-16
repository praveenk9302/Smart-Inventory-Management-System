from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


from django.db import models
from django.utils import timezone

class Sale(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_sold = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    

from django.db import models

class SalesHistory(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold}"
