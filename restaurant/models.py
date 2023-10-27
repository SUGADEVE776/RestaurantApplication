from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class RestaurantFeature(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Restaurants(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    opening_time = models.TimeField(default='00:00:00')
    closing_time = models.TimeField(default='00:00:00')
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    features = models.ManyToManyField(RestaurantFeature,blank=True)

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
    description = models.TextField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    mealtime = models.ForeignKey(MealTime, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('restaurant', 'name'),)

    def __str__(self):
        return self.name


class Dish_Quantity(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dishes, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.restaurant} - {self.dish}"

    class Meta:
        unique_together = (('restaurant', 'dish'),)


class Feedback(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, related_name='restaurant')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review = models.TextField()

    class Meta:
        unique_together = (('restaurant', 'user'),)

    def __str__(self):
        return self.restaurant.name


class Dish_Feedback(models.Model):
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review = models.TextField()
    dish = models.ForeignKey(Dishes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user', 'rating', 'review'), ('user', 'rating'), ('user', 'review'), ('rating', 'user'),
            ('rating', 'review'), ('review', 'user'),
            ('review', 'rating'), ('user',), ('rating',), ('review',))


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


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class User_Address(models.Model):
    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    door_no = models.CharField(max_length=10)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)

    class Meta:
        # Ensure a user can have only one 'home' address
        unique_together = ('user', 'address_type')
        # Ensure that 'other' addresses are not unique
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'address_type'],
                condition=models.Q(address_type='home'),
                name='unique_home_address'
            )
        ]

    def __str__(self):
        return self.door_no + self.street_address + self.city + self.state


class Offers(models.Model):
    restaurant = models.OneToOneField(Restaurants, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    value = models.IntegerField()
    expiry_date = models.DateTimeField(default=None, null=True)
    status = models.BooleanField(default=True)

    def is_expired(self):
        now = timezone.now()
        if self.expiry_date and now > self.expiry_date:
            self.status = False
            self.save()
            return True
        return False


# class Cart(models.Model):


class Tables_Available(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    # availability = models.BooleanField(default=True)
    breakfast = models.IntegerField(default=10)
    lunch = models.IntegerField(default=10)
    dinner = models.IntegerField(default=10)
    date = models.DateField()

    class Meta:
        unique_together = ['restaurant', 'date']


class User_DineIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    mealtime_choices = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]
    mealtime = models.CharField(max_length=20, choices=mealtime_choices)
    date = models.DateField()
    table = models.IntegerField()

    class Meta:
        unique_together = ['restaurant', 'date', 'mealtime']


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)



class Cart_Items(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Dish_Quantity, on_delete=models.CASCADE)
    nos = models.IntegerField(default=1)


class Checkout(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.ForeignKey(User_Address, on_delete=models.SET_NULL, null=True, blank=True)
    applied_coupon = models.ForeignKey(Offers, on_delete=models.SET_NULL, null=True, blank=True)



class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_cost = models.IntegerField()
    address = models.CharField(max_length=100)
    order_time = models.DateTimeField(auto_now_add=True)


class Reward(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    value = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)


