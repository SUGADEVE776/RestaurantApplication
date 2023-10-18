from django.contrib import admin
from django.contrib.auth.models import User
from .models import *


# Register your models here.

class Restaurant_admin(admin.ModelAdmin):
    list_display = ['name', 'location']


class Bookmark_admin(admin.ModelAdmin):
    list_display = ['user', 'restaurant']


class Dishes_admin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description', 'category', 'mealtime', 'restaurant']


admin.site.register(Restaurants, Restaurant_admin)
admin.site.register(Feedback)
admin.site.register(Bookmarks, Bookmark_admin)
admin.site.register(OneTimePassword)
admin.site.register(Dishes,Dishes_admin)
admin.site.register(MealTime)
admin.site.register(Category)
admin.site.register(Dish_Feedback)
admin.site.register(Dish_Quantity)