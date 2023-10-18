from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Restaurants(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1,default=0.0)


    def __str__(self):
        return self.name


class MealTime(models.Model):
    CHOICES = [('BREAKFAST', 'BREAKFAST'), ('LUNCH', 'LUNCH'), ('DINNER', 'DINNER'), ('SNACK', 'SNACK'),
               ('DESSERT', 'DESSERT')]
    name = models.CharField(max_length=100, choices=CHOICES, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    CHOICES = [
        ('VEGETARIAN', 'vegetarian'),
        ('NON-VEGETARIAN', 'non-vegetarian')
    ]

    name = models.CharField(max_length=30, choices=CHOICES, null=True)

    def __str__(self):
        return self.name


class Dishes(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    mealtime = models.ForeignKey(MealTime, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('restaurant','name'),)

    def __str__(self):
        return self.name

class Dish_Quantity(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dishes, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return self.quantity


class Feedback(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, related_name='restaurant')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review = models.TextField()

    class Meta:
        unique_together = (('restaurant','user'),)

    def __str__(self):
        return self.restaurant.name


class Dish_Feedback(models.Model):
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review = models.TextField()
    dish = models.ForeignKey(Dishes, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        unique_together = (
    ('user', 'rating', 'review'),('user', 'rating'), ('user', 'review'),('rating', 'user'),('rating', 'review'),('review', 'user'),
    ('review', 'rating'),('user',),('rating',),('review',))


class Bookmarks(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'restaurant'], name='unique_bookmarks')
        ]


class OneTimePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()
