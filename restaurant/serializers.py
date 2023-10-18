from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class Feedback_serializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('rating','review','restaurant','user')
        depth=1


class Restaurant_serializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurants
        fields = '__all__'
        depth = 1


class Bookmark_serializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmarks
        fields = '__all__'
        depth = 1


class Combined_Serializer(serializers.Serializer):
    restaurant = Restaurant_serializer()
    feedback = Feedback_serializer()


class Dishes_serializer(serializers.ModelSerializer):
    class Meta:
        model = Dishes
        fields = '__all__'
        depth = 1

