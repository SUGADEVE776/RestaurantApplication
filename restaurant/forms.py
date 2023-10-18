from django import forms
from django.contrib.auth.forms import *
from django.contrib.auth.models import User
from .models import *

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username','email','password1')


class Edit_UserForm(forms.Form):
    class Meta:
        model = User
        fields = '__all__'


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class EditRestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurants
        fields = '__all__'


class UserEditReviewForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('rating','review')