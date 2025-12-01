from django.urls import path
from .views import Signup,Login,Package_details,RateReviewAPI,Index,Navbar,Footer,Payment,Payment_Success,Package_BookingAPI,front_end_signup,front_end_login,Package_list,My_Booking,LogoutView,Package_Booking_Frontend

urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('package_details/', Package_details.as_view(), name='Package_details'),
    path('reviews/', RateReviewAPI.as_view(), name='reviews'),
    path('index/', Index.as_view(), name='index'),
    path('navbar/', Navbar.as_view(), name='navbar'),
    path('footer/', Footer.as_view(), name='footer'),
    path('payment/', Payment.as_view(), name='payment'),
    path('payment_success/', Payment_Success.as_view(), name='payment sucess'),
    path('package_bookings/', Package_BookingAPI.as_view()),
    # path('bookings/<int:pk>/', Package_BookingAPI.as_view()),  
    path('frontend_signup/', front_end_signup.as_view(), name='frontendsignup'),
    path('frontend_login/', front_end_login.as_view(), name='frontend login'),
    path('package_list/', Package_list.as_view(), name='package list'),
    path('my_booking/', My_Booking.as_view(), name='my booking'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('package_booking_frontend/', Package_Booking_Frontend.as_view(), name='package booking frontend')
]
