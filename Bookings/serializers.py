from rest_framework import serializers
from restaurant.models import *


class Table_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Tables_Available
        fields = '__all__'


class Dine_in_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_DineIn
        fields = '__all__'
