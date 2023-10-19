import random
from django.http import HttpResponse,response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .serializers import *
from .models import *
from rest_framework import viewsets
from rest_framework.response import Response
from django.views import generic
from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from .forms import CustomUserCreationForm, Edit_UserForm, UserChangeForm
from django.views.generic import ListView,UpdateView
from rest_framework import generics
from email.message import EmailMessage
from django.urls import reverse_lazy
import smtplib
import ssl


def admin_home(request):
    return render(request, 'Admin/base.html')


def Register_and_Login(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if len(request.POST) > 3:

            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                firstname = form.cleaned_data['first_name']
                lastname = form.cleaned_data['last_name']
                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']

                print(username, email, firstname, lastname, password1, password2)

                if not User.objects.filter(username=username).exists() and not User.objects.filter(
                        email=email).exists():
                    if password1 != password2:
                        return render(request, 'Registration/RegAndLogin.html',
                                      {'form': form, 'error_message': 'Password not matching'})
                    user = User.objects.create_user(username=username, email=email, password=password1,
                                                    first_name=firstname, last_name=lastname)
                    messages.success(request, "Registration successful! You can now log in.")
                    # login(request, user)
                    return redirect('/register/')
                else:
                    return render(request, 'Registration/RegAndLogin.html',
                                  {'form': form, 'error_message': 'Username or email already exists.'})

        if len(request.POST) == 3:
            print(request.POST)
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                x = login(request, user)
                print(x)
                return redirect('/restaurant/')
            else:
                messages.success(request, ('Incorrect Credentials'))
                return redirect('/register/')
    else:
        form = CustomUserCreationForm()

    return render(request, 'Registration/RegAndLogin.html', {'form': form})





def login_admin(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None and User.objects.filter(username=username).exclude(is_superuser=False):
            login(request, user)
            return redirect('/admin_home/')
        else:
            messages.success(request, ('Error'))
            return redirect('login_admin/')
    else:
        return render(request, 'Login/admin_login.html', {})


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@login_required(login_url=Register_and_Login)
def UserAPI(request, pk=None):
    if request.method == 'GET':
        if pk is not None:
            users = User.objects.filter(id=pk)

            return render(request, 'Admin/specificuser.html', {'userlist': users})
        # if request.GET.get('')
        else:
            users = User.objects.all().exclude(is_superuser=True)
            # serializer = UserSerializer(users, many=True)
            # return Response(serializer.data)
            return render(request, 'Admin/userview.html', {'userlist': users})

    elif request.method == 'POST':
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': "Member Added",
                'data': serializer.data
            })

        return Response(serializer.errors)

    elif request.method == 'PUT':
        data = request.data
        try:
            user = User.objects.get(id=data['id'])
        except User.DoesNotExist:
            return Response({
                "message": "User not found"
            }, status=404)

        serializer = UserSerializer(user, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Updated Successfully"
            })

        return Response(serializer.errors)

    elif request.method == 'PATCH':
        data = request.data
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({
                "message": "User not found"
            }, status=404)

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Partially Updated Successfully"
            })

        return Response(serializer.errors)

    elif request.method == 'DELETE':
        data = request.data
        try:
            user = User.objects.get(id=data['id'])
        except User.DoesNotExist:
            return Response({
                "message": "User not found"
            }, status=404)

        user.delete()
        return Response("Data Deleted")


@login_required(login_url=Register_and_Login)
def Restaurant_list(request):
    print(request.GET)
    print(request.GET.getlist('request'))
    all = Feedback.objects.all()
    print(all)
    rating_filter = request.GET.get('rating')
    location_filter = request.GET.get('location')
    print(location_filter)

    if rating_filter:
        all = Feedback.objects.filter(rating__gt=float(rating_filter))
        print(all)

    if location_filter:
        restaurant = Restaurants.objects.filter(location__icontains=location_filter) #will have two objects
        print(restaurant)
        for i in restaurant:
            feedback = Feedback.objects.filter(restaurant=restaurant) #to loop through it
            print(feedback)

            # <QuerySet [<Feedback: Thalappakatti>, <Feedback: Aasife>]>  i need result like this

    if request.GET.getlist('request') == ['bookmark']:
        user = request.user  # Assuming you're using authentication
        all = Restaurants.objects.filter(bookmarks__user=user)

    p = Paginator(all, 2)
    pages = request.GET.get('page')
    all = p.get_page(pages)

    return render(request, 'Dashboard/restaurants.html', {'restaurant_list': all})


def Bookmark_restaurant(request):
    user = request.user
    if request.method == 'POST':
        for restaurant_name in request.POST.getlist('restaurant_selection'):
            user = User.objects.get(username=user)
            restaurant = Restaurants.objects.get(name=restaurant_name)
            try:
                bookmark = Bookmarks.objects.create(user=user, restaurant=restaurant)
            except:
                return Response({"message": "Already Bookmarked the restaurant."})

    return Response("Done")



def Edit_User(request):
    if request.method == 'POST':
        form = Edit_UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                # login(request, user)
                return redirect('restaurant/')
            else:
                return render(request, 'Admin/useredit.html',
                              {'form': form, 'error_message': 'Username or email already exists.'})
    else:
        form = CustomUserCreationForm()

    return render(request, 'Admin/useredit.html', {'form': form})

def admin_user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a success page, login page, or any other desired page
            return redirect('/admin_home/User/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def email_send(emails, sub, bod):
    email_sender = "sugdev2000@gmail.com"
    email_password = "ttiw ochg dmew diim"

    email_reciever = emails

    email_cc = 'sugakldm@gmail.com'
    # email_bcc = str(input("bcc?:"))

    subject = sub

    body = bod

    em = EmailMessage()
    em['from'] = email_sender
    em['to'] = email_reciever
    em['cc'] = email_cc
    # em['bcc'] = email_bcc
    em['subject'] = subject

    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail([email_sender], [email_reciever, email_cc], em.as_string())

    print("Email sent Successfully")


def forgot_password_phone(request):
    if request.method == 'POST':
        username = request.POST["username"]
        user = User.objects.get(username=username)
        print(username)
        gen_otp = random.randint(100000, 999999)

        save_otp = OneTimePassword.objects.create(user=user, otp=gen_otp)

        # return redirect(forgot_password_email)


    else:
        return render(request, 'Login/user_login.html', {})


def forgot_password_email(request):
    if request.method == 'POST':
        # import pdb
        # pdb.set_trace()
        print(request.POST)
        email = request.POST['email']
        request.session['email'] = email
        print(email)
        try:
            user = User.objects.get(email=email)
        except:
            messages.success(request, message='No User with this email found')
            return render(request, 'Login/forgot_password_email.html', )
        print(user)
        gen_otp = random.randint(100000, 999999)
        if user:
            save_otp = OneTimePassword.objects.create(user=user, otp=gen_otp)
            sub = "OTP for Changing Password"
            message = f"""Greetings  from Restaurant APP
                    OTP for changing your password is
                    {gen_otp}
                    
                    Have a Good day
                    
                    Thank you
                    """

            email_send(emails=email, sub=sub, bod=message)
            return redirect('/reset/')

        else:
            return HttpResponse('No User with this email found')

    return render(request, 'Login/forgot_password_email.html', {})


def otp_validation_and_reset(request):
    if request.method == 'POST':
        try:
            import pdb
            pdb.set_trace()
            user = User.objects.get(email=request.session['email'])
            obj = OneTimePassword.objects.get(user=user)
            if obj.otp == int(request.POST['otp']):
                obj.delete()
                if request.POST['password1'] == request.POST['password2']:
                    user.set_password(request.POST['password1'])
                    user.save()
                    # messages.success(request,{'message'} )
                    return Response({'message': 'Password reset success'})
                else:
                    messages.success(request, 'Password is not matching')

            else:
                return Response({"message": "wrong otp"}, status=403)

        except:
            return Response({"message": "otp not exist"}, status=403)

    return render(request, 'Login/reset_password.html')


def forgot_username(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        try:
            user = User.objects.get(email=email)
            request.session['email'] = email
        except:
            messages.success(request, message='No User with this email found')
            return render(request, 'Login/forgot_username_email.html', )
        print(user)
        gen_otp = random.randint(100000, 999999)
        if user:
            save_otp = OneTimePassword.objects.create(user=user, otp=gen_otp)
            sub = "OTP for Changing Password"
            message = f"""Greetings  from Restaurant APP
                    OTP for changing your password is
                    {gen_otp}
                    
                    Have a Good day
                    
                    Thank you
                    """

            email_send(emails=email, sub=sub, bod=message)
            return redirect('/usernameotp/')

        else:
            return HttpResponse('No User with this email found')

    return render(request,'Login/forgot_username_email.html')

def otp_validation_for_username(request):
    if request.method == 'POST':
        try:
            # import pdb
            # pdb.set_trace()
            user = User.objects.get(email=request.session['email'])
            print('session' == user)
            obj = OneTimePassword.objects.get(user=user)
            if obj.otp == int(request.POST['otp']):
                obj.delete()
                sub = "Request for Forgot Username"
                message = f"""  Greetings  from Restaurant APP
                            Your Username is
                            {user}  
                            
                            Have a Good day
                            
                            Thank you
                    """

                email_send(emails=request.session['email'], sub=sub, bod=message)

                return redirect('/register/')

            else:
                return HttpResponse({"message": "wrong otp"}, status=403)

        except:
            return HttpResponse({"message": "otp not exist"}, status=403)

    return render(request, 'Login/UsernameOtpValidation.html')

class UserUpdateByAdmin(generic.UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'Admin/userupdatebyadmin.html'
    success_url = reverse_lazy('edit_user/')


class RestaurantUpdateByAdmin(generic.UpdateView):
    model = Restaurants
    template_name = 'Admin/restaurantupdatebyadmin.html'
    fields = '__all__'
    success_url = reverse_lazy('restauran')

class Restaurant_list_admin(generics.ListAPIView):
    queryset = Restaurants.objects.all()
    serializer_class = Restaurant_serializer

    def list(self,request):
        print(request.POST)
        all_restaurants = self.get_queryset()

        filter_value = request.GET.get('rating')
        location_filter = request.GET.get('location')

        if filter_value:
            all_restaurants = all_restaurants.filter(avg_rating__gt=float(filter_value))

        if location_filter:
            all_restaurants = all_restaurants.filter(location__icontains=location_filter)
        

        # if request.GET.getlist('request') == ['bookmark']:
        #     user = request.user  # Assuming you're using authentication
        #     all = Restaurants.objects.filter(bookmarks__user=user)

        p = Paginator(all_restaurants, 5)
        pages = request.GET.get('page')
        all_restaurants = p.get_page(pages)

        return render(request, 'Admin/list_restaurant.html', {'restaurant_list': all_restaurants})


class restaurant_by_location(APIView):
    def post(self, request):
        location = request.data.get('location')  # Use request.data to access POST data
        restaurants = Restaurants.objects.filter(location__icontains=location)
        serialized_data = Restaurant_serializer(restaurants, many=True)
        return Response({serialized_data})

class RestaurantDetails(APIView):
    def get(self, request, pk):
        try:
            restaurant = Restaurants.objects.get(pk=pk)
            feedback = Feedback.objects.filter(restaurant=restaurant)
        except Restaurants.DoesNotExist:
            return Response({"message": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        restaurant_serializer = Restaurant_serializer(restaurant)
        feedback_serializer = Feedback_serializer(feedback, many=True)

        all = {
            "name": restaurant_serializer.data['name'],
            "location": restaurant_serializer.data['location'],
            "feedback": feedback_serializer.data
        }
        return Response(all)
        #return render(request, 'Dashboard/restaurant_list.html',{'restaurants' : all})



class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurants.objects.all()
    serializer_class = Restaurant_serializer



class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = Feedback_serializer


class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmarks.objects.all()
    serializer_class = Bookmark_serializer


class DishesViewSet(viewsets.ModelViewSet):
    queryset = Dishes.objects.all()
    serializer_class = Dishes_serializer


class RestaurantList(generics.ListAPIView):
    queryset = Restaurants.objects.all()
    serializer_class = Restaurant_serializer


    def list(self, request):
        # Fetch the restaurant list
        print(request.POST)
        all_restaurants = self.get_queryset()

        filter_value = request.GET.get('rating')
        location_filter = request.GET.get('location')

        if filter_value:
            all_restaurants = all_restaurants.filter(avg_rating__gt=float(filter_value))

        if location_filter:
            all_restaurants = all_restaurants.filter(location__icontains=location_filter)
        
        # You can add filtering logic here based on request.GET parameters
        # Example: location = request.GET.get('location')
        # Example: rating = request.GET.get('rating')

        # Render the HTML template and pass the context data

        p = Paginator(all_restaurants, 4)
        pages = request.GET.get('page')
        all_restaurants = p.get_page(pages)

        return render(request, 'Dashboard/restaurant_list.html', {'restaurant_list': all_restaurants})


class reviews_by_users(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = Feedback_serializer
    
    def list(self, request,pk):
        all_restaurants = self.get_queryset()
        print(all_restaurants)

        all = all_restaurants.filter(restaurant__id=pk).values('review','user_id')
        print(all)


        return render(request, 'Dashboard/specific_restaurant.html', {'comments': all})



class dishes_by_restaurants(generics.ListAPIView):
    queryset = Dishes.objects.all()
    serializer_class = Dishes_serializer

    def list(self, request,pk):
        all_restaurants = self.get_queryset()
        print(all_restaurants)

        all = all_restaurants.filter(restaurant__id=pk).values('name')
        print(all)

        return render(request, 'Dashboard/specific_restaurant.html', {'dishes': all})





class list_bookmarks(generics.ListAPIView):
    serializer_class = Bookmark_serializer
    

    def get_queryset(self):
        user = self.request.user
        return Bookmarks.objects.filter(user=user).values('restaurant')

    def list(self, request):
        queryset = self.get_queryset()
        print(queryset)
        x = []
        restaurant_ids = queryset.values_list('restaurant', flat=True)
        restaurants = Restaurants.objects.filter(id__in=restaurant_ids)

        for res in restaurants:
            x.append(res.name)
        return render(request, 'Dashboard/bookmarked_restaurants.html',{'bookmarks': x})



