from django.urls import path
from .views import Signup,Login,Package_details,RateReview,Index,Navbar,Footer,Payment,Payment_Success

urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('package_details/', Package_details.as_view(), name='Package_details'),
    path('reviews/', RateReview.as_view(), name='reviews'),
    path('index/', Index.as_view(), name='index'),
    path('navbar/', Navbar.as_view(), name='navbar'),
    path('footer/', Footer.as_view(), name='footer'),
    path('payment/', Payment.as_view(), name='payment'),
    path('payment_success/', Payment_Success.as_view(), name='payment_sucess'),

]
