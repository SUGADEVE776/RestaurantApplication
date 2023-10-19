"""
URL configuration for RestaurantApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from restaurant import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', views.UserProfileViewSet)
router.register(r'Restaurant', views.RestaurantViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'bookmark', views.BookmarkViewSet)
router.register(r'dishes', views.DishesViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login_admin/', views.login_admin),
    path('admin_home/', views.admin_home),
    path('register/', views.Register_and_Login),
    # path('restaurant/',views.Restaurant_API),
    path('forgot/', views.forgot_password_phone),
    path('forgotmail/', views.forgot_password_email),
    # path('verify/', views.verify_email_otp),
    path('reset/', views.otp_validation_and_reset),
    path('forgotusername/', views.forgot_username),
    path('usernameotp/', views.otp_validation_for_username),
    path('admin_home/User/', views.UserAPI),
    path('admin_home/User/<int:pk>', views.UserUpdateByAdmin.as_view()),
    path('admin_home/Restaurant', views.Restaurant_list_admin),
    path('admin_home/Restaurant/<int:pk>', views.RestaurantUpdateByAdmin.as_view()),
    # path('list/', views.RestaurantListView.as_view()) 
    path('login_admin/', views.login_admin),
    path('restaurant/', views.RestaurantList.as_view(), name='restaurant-list'),
    # path('restaurant/<int:pk>', views.FeedbackUpdate),
    path('edit/', views.Edit_User),
    path('restaurant/bm/', views.Bookmark_restaurant),
    path('restaurant/bookmarks/', views.list_bookmarks.as_view()),
    path('restaurant/comments/<int:pk>', views.reviews_by_users.as_view()),
    path('restaurant/dishes/<int:pk>', views.dishes_by_restaurants.as_view()),
    path('restaurant/dishes/',views.dishes_by_restaurants.as_view()), 
    # path('edit_user/',views.UserUpdateByAdmin.as_view()),
    path('edit_restaurant/',views.RestaurantUpdateByAdmin.as_view()),
    path('location/', views.restaurant_by_location.as_view()),
    path('whole/',views.RestaurantDetails.as_view()),
    path('whole/<int:pk>',views.RestaurantDetails.as_view()),
    # path('combine/<int:pk>', views.CombinedDataAPIView.as_view())
    # path('sss/', views.RestaurantList.as_view(), name='restaurant-list'),


    
]
urlpatterns += router.urls
