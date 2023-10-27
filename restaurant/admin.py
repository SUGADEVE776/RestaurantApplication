from django.contrib import admin
from django.contrib.auth.models import User
from .models import *


# Register your models here.

class Restaurant_admin(admin.ModelAdmin):
    list_display = ['name', 'location', 'opening_time', 'closing_time']


class Bookmark_admin(admin.ModelAdmin):
    list_display = ['user', 'restaurant']


class Dishes_admin(admin.ModelAdmin):
    list_display = ['name', 'description', 'category', 'mealtime', 'restaurant']


class Feedback_admin(admin.ModelAdmin):
    list_display = ('restaurant', 'rating', 'user')


class Address_admin(admin.ModelAdmin):
    list_display = ('user', 'address_type')


class OrderHistory_admin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_cost')


admin.site.register(Restaurants, Restaurant_admin)
admin.site.register(Feedback, Feedback_admin)
admin.site.register(Bookmarks, Bookmark_admin)
admin.site.register(OneTimePassword)
admin.site.register(Dishes, Dishes_admin)
admin.site.register(MealTime)
admin.site.register(Category)
admin.site.register(Dish_Feedback)
admin.site.register(Dish_Quantity)
admin.site.register(Wallet)
admin.site.register(Offers)
admin.site.register(Tables_Available)
admin.site.register(User_DineIn)
admin.site.register(User_Address, Address_admin)
admin.site.register(Cart)
admin.site.register(Cart_Items)
admin.site.register(Checkout)
admin.site.register(RestaurantFeature)
admin.site.register(OrderHistory,OrderHistory_admin)
