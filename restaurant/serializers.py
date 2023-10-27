from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class Feedback_serializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Feedback
        fields = ('restaurant', 'user', 'rating', 'review')


class Restaurant_serializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurants
        fields = '__all__'


class Bookmark_serializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmarks
        fields = ('restaurant', 'user')


class Dishes_serializer(serializers.ModelSerializer):
    class Meta:
        model = Dishes
        fields = '__all__'
        # depth = 1


class Dish_Quantity_serializer(serializers.ModelSerializer):
    class Meta:
        model = Dish_Quantity
        fields = '__all__'
        # depth = 1


class Register_serializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            return serializers.ValidationError({"Message": "Password not matching"})

        else:
            user.set_password(password)
            user.save()

        return user


class Wallet_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class Offer_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Offers
        fields = '__all__'


class CartItem_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_Items
        fields = '__all__'
