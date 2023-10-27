import datetime
import random
from django.db.models import Avg
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from rest_framework.response import Response

from RestaurantApp import settings
from .serializers import *
from .models import *
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from django.views import generic
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, Edit_UserForm, UserChangeForm
from django.views.generic import ListView, UpdateView
from rest_framework import generics
from email.message import EmailMessage
from django.urls import reverse_lazy
import smtplib
import ssl
import razorpay


class RegisterAPI(APIView):
    def post(self, request):
        print(request.data)
        serializers = Register_serializer(data=request.data)
        data = {}
        if serializers.is_valid():
            user = serializers.save()
            token = Token.objects.create(user=user)
            data['email'] = user.email
            data['username'] = user.username

        else:
            data = serializers.errors

        return Response(data)


class LoginAPI(APIView):
    def post(self, request):
        import pdb
        pdb.set_trace()
        username = request.data['username']
        password = request.data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

        else:
            return Response({"message": "User not found"})

        return Response({
            "Token": token.key
        })


class RestaurantAPI(APIView):
    def get(self, request, pk=None):
        import pdb
        pdb.set_trace()
        rating = request.GET.get('rating')
        location = request.GET.get('location')
        features = request.GET.get('features')

        if pk:
            restaurant = Restaurants.objects.filter(pk=pk)
            serializer = Restaurant_serializer(restaurant, many=True)
            return Response(serializer.data)

        if rating:
            restaurant = Restaurants.objects.filter(avg_rating__gt=rating)
            serializer = Restaurant_serializer(restaurant, many=True)
            return Response(serializer.data)

        if location:
            restaurants = Restaurants.objects.filter(location__icontains=location)
            if not restaurants:
                return Response({"message": "No Matching Restaurants in this locations"})
            serializer = Restaurant_serializer(restaurants, many=True)
            return Response(serializer.data)

        if features:
            features = RestaurantFeature.objects.get(name=features)
            restaurant = Restaurants.objects.filter(features=features.id)
            serializer = Restaurant_serializer(restaurant, many=True)
            return Response(serializer.data)

        if 'now' in request.GET:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            restaurant = Restaurants.objects.filter(opening_time__lte=current_time,closing_time__gte=current_time)
            serializer = Restaurant_serializer(restaurant, many=True)
            return Response(serializer.data)

        else:
            restaurant = Restaurants.objects.all()
            serializer = Restaurant_serializer(restaurant, many=True)
            return Response(serializer.data)


class Feedback_RestaurantAPI(APIView):
    def get(self, request):
        feedback = Feedback.objects.all()
        serializer = Feedback_serializer(feedback, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = Feedback_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            avg = Feedback.objects.filter(restaurant=data['restaurant']).aggregate(Avg('rating'))['rating__avg']
            avg = round(avg, 1)
            res = Restaurants.objects.get(id=data['restaurant'])
            res.avg_rating = avg
            res.save()
        else:
            return Response(serializer.errors)

        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        old_data = Feedback.objects.filter(id=pk)
        serializer = Feedback_serializer(old_data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


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


class Forgot_passwordAPI(APIView):
    def post(self, request):
        email_id = request.data['email']

        try:
            user = User.objects.get(email=email_id)
            otp = random.randrange(100000, 999999)
            save_otp = OneTimePassword.objects.create(user=user, otp=otp)

            print(otp, "otp")
            sub = "OTP for Verification"
            message = f"""Greetings from Restaurant App

            Hello there! We're here to assist you with the password change process for your Restaurant App account.

            To proceed with changing your password, you will need to verify your identity by entering the following OTP (One-Time Password):

            OTP for changing your password: {otp}

            Please enter this OTP in the provided field within the app to initiate the password change process. Make sure to keep it confidential to maintain the security of your account.

            If you did not request this change or have any concerns, please contact our customer support immediately.

            Have a fantastic day, and thank you for choosing Restaurant App for your dining needs!

            Best regards,
            The Restaurant App Team
            """

            email_send(emails=email_id, sub=sub, bod=message)
        except:
            return Response({"message": "email not found"}, status=403)

        return Response({"message": "email sent successfull......"})


class Verify_otpAPI(APIView):
    def post(self, request):
        try:
            # import pdb
            # pdb.set_trace()
            user = User.objects.get(email=request.data['email'])
            obj = OneTimePassword.objects.filter(user=user).last()
            if obj.otp == int(request.data['otp']):
                obj.delete()
                return Response({"message": "otp verified"})
            else:
                return Response({"message": "wrong otp"}, status=403)

        except:
            return Response({"message": "otp not exist"}, status=403)


class Reset_PasswordAPI(APIView):
    def post(self, request):

        try:
            user = User.objects.get(email=request.data['email'])
        except:
            try:
                user = User.objects.get(email=request.data['email'])
            except:
                return Response({"message": "email not found"}, status=403)
        if request.data['password'] == request.data['password2']:
            user.set_password(request.data['password'])
            user.save()
            return Response({'message': 'Password reset success'})

        else:
            return Response({'message': 'Password not matching'})


class Bookmark_restaurantAPI(APIView):
    def post(self, request):
        serializer = Bookmark_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "Bookmarked Sucessfully"})

        else:
            return Response(serializer.errors)


class Cart_API(APIView):
    def post(self, request):
        import pdb
        pdb.set_trace()
        # {
        #     "cart": 3,
        #     "item": 6,
        #     "nos": 2
        # }
        serializer = CartItem_Serializer(data=request.data)
        if serializer.is_valid():
            item = serializer.validated_data['item']
            nos = serializer.validated_data['nos']

            avail = Dish_Quantity.objects.get(id=item.id)
            if avail.quantity > nos:
                avail.quantity -= nos
                avail.save()
                serializer.save()

                return Response({"Sucessfully added to the Cart"})
            else:
                return Response({"Out of Stock"})

        else:
            return Response(serializer.errors)


class Checkout_API(APIView):
    def post(self, request):
        import pdb
        pdb.set_trace()
        # {
        #     "cart": 3,
        #     "delivery_address": 1,
        #     "applied_coupon": 1
        # }
        items = Cart_Items.objects.filter(cart=request.data['cart'])
        total_cost = 0

        for i in items:
            total_cost += i.item.price * i.nos

        if request.data['applied_coupon']:
            offer = Offers.objects.get(id=request.data['applied_coupon'])
            discount_amount = total_cost * (offer.value / 100)
            total_cost -= discount_amount
            coupon = Offers.objects.get(id=request.data['applied_coupon'])

        else:
            coupon = None

        checkout = Checkout.objects.create(
            cart=Cart.objects.get(id=request.data['cart']),
            total_cost=total_cost,
            delivery_address=User_Address.objects.get(id=request.data['delivery_address']),
            applied_coupon=coupon,
        )

        return Response({"checkout"})


razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


class PaymentsAPI(APIView):
    def post(self, request, pk):
        import pdb
        pdb.set_trace()
        currency = 'INR'

        # Retrieve the total cost from the Checkout model for the given cart pk
        try:
            total_cost = (Checkout.objects.get(cart=pk)).total_cost
        except Checkout.DoesNotExist:
            return Response({'error': 'Checkout not found'}, status=status.HTTP_404_NOT_FOUND)

        # Convert the amount to paise (multiply by 100)
        amount = int(total_cost * 100)

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': 0  # 0 to capture payment manually, 1 to capture automatically
        })

        razorpay_order_id = razorpay_order['id']

        # Create a context dictionary to pass to the template
        context = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': currency
        }

        # Render the 'razorpay/index.html' template with the context
        return render(request, 'razorpay/index.html', context)


class Payment_API(APIView):
    def post(self, request, pk):
        import pdb
        pdb.set_trace()
        # {
        #     "cart": 3,
        #     "amount": 1112
        # }
        total = (Checkout.objects.get(cart=pk)).total_cost
        address_id = (Checkout.objects.get(cart=pk)).delivery_address_id
        address = User_Address.objects.get(id=address_id)
        if request.data['amount'] == total:
            user = (Cart.objects.get(id=pk)).user
            door_no = address.door_no
            street_address = address.street_address
            city = address.city
            state = address.state
            postal_code = address.postal_code
            address = f"{door_no}, {street_address}, {city}, {state} {postal_code}"

            OrderHistory.objects.create(
                user=user,
                address=address,
                total_cost=total,

            )
            cart_items = Cart_Items.objects.filter(cart=pk)
            checkout = Checkout.objects.filter(cart=pk)
            cart_items.delete()
            checkout.delete()

            return Response({"message": "Payment Sucessful, Order Placed"})

        else:
            return Response({"message": "Payment Not Sucessful"})


class ScratchCard(APIView):
    def post(self, request):
        import pdb
        pdb.set_trace()
        user_id = 6
        order_history = OrderHistory.objects.filter(user_id=user_id).order_by('-order_time')
        count = len(order_history)
        total = 0
        if count % 3 == 0:
            i = 0
            while (i < 2):
                i += 1
                total += order_history[i].total_cost

            scratch_amount = total * 0.03
            Reward.objects.create(
                user=User.objects.get(id=user_id),
                value=scratch_amount,
            )

        else:
            return Response({"Better luck Next Time"})

        return Response({"message": "Won a scratch Card"})


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


class DishQuantityViewSet(viewsets.ModelViewSet):
    queryset = Dish_Quantity.objects.all()
    serializer_class = Dish_Quantity_serializer




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


# @api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
# @login_required(login_url=Register_and_Login)
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


# @login_required(login_url=Register_and_Login)
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
        restaurant = Restaurants.objects.filter(location__icontains=location_filter)  # will have two objects
        print(restaurant)
        for i in restaurant:
            feedback = Feedback.objects.filter(restaurant=restaurant)  # to loop through it
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

    return render(request, 'Login/forgot_username_email.html')


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


class FeedbackUpdateView(UpdateView):
    model = Feedback
    template_name = 'Dashboard/edit_feedback.html'
    fields = ('rating', 'review')

    # success_url = reverse_lazy('/restaurant/')  # Replace 'review/' with the appropriate URL name for redirection

    def form_valid(self, form):
        rating = form.cleaned_data.get('rating')
        review = form.cleaned_data.get('review')

        print(review, rating)

        print(self.request.user)
        return super().form_valid(form)


class Restaurant_list_admin(generics.ListAPIView):
    queryset = Restaurants.objects.all()
    serializer_class = Restaurant_serializer

    def list(self, request):
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
        # return render(request, 'Dashboard/restaurant_list.html',{'restaurants' : all})





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

    def list(self, request, pk):
        all_restaurants = self.get_queryset()
        print(all_restaurants)

        all = all_restaurants.filter(restaurant__id=pk).values('review', 'user_id')
        print(all)

        return render(request, 'Dashboard/specific_restaurant.html', {'comments': all})


class dishes_by_restaurants(generics.ListAPIView):
    queryset = Dishes.objects.all()
    serializer_class = Dishes_serializer

    def list(self, request, pk):
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
        return render(request, 'Dashboard/bookmarked_restaurants.html', {'bookmarks': x})


class Add_Money(APIView):
    def post(self, request, ):
        # serializer = Wallet_Serializer(data=request.data)
        import pdb
        pdb.set_trace()
        # if serializer.is_valid():
        wallet = Wallet.objects.get(user=request.data['user'])

        wallet.balance += request.data['balance']
        wallet.save()
        return Response({"Message": "Amount Added to Wallet"})
