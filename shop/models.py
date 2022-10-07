from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

PAYMENT = [
    (1, "Za pobraniem"),
    (2, "Przelew")
]
STATUS = [
    (1, 'W trakcie przygotowania'),
    (2, "Oczekujące na płatność"),
    (3, "Zrealizowane"),
]


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.name}'


class Products(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    categories = models.ManyToManyField(Category, through="ProductCategory")
    number_of_items = models.IntegerField()


class ProductCategory(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Image(models.Model):
    name = models.CharField(max_length=64)
    path = models.CharField(max_length=256)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)


class Delivery(models.Model):
    address = models.CharField(max_length=256)
    payment_method = models.IntegerField(choices=PAYMENT)

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,default=1)
    address = models.CharField(max_length=256)


class Basket(models.Model):
    products = models.ManyToManyField(Products, through='ProductBasket')
    my_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    delivery_method = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS)


class ProductBasket(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
