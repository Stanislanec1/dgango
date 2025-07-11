from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Таблица docs
class Document(models.Model):
    file_path = models.CharField(max_length=255)
    size = models.FloatField()  # в КБ

    def __str__(self):
        return f"Document {self.id}"

# Таблица users_to_docs
class UserToDocument(models.Model):
    username = models.CharField(max_length=150)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.username} -> Document {self.document.id}"

# Таблица price
class Price(models.Model):
    file_type = models.CharField(max_length=20)
    price = models.FloatField()

    def __str__(self):
        return f"{self.file_type}: {self.price} per KB"

# Таблица cart
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.id} | User: {self.user.username} | Paid: {self.payment}"
