from django.urls import path
from .views import Login,BusAPI,RouteAPI
from .views import PackageDetailsView,MessageListView

urlpatterns = [
    
    path('login/', Login.as_view(), name='login'),
    path('bus/', BusAPI.as_view()),          
    path('bus/<int:pk>/', BusAPI.as_view()),  
    path('route/', RouteAPI.as_view()),           
    path('route/<int:pk>/', RouteAPI.as_view()),
    path("package_details/", PackageDetailsView.as_view(), name="Package_details"),
    path('messages/', MessageListView.as_view(), name='messages'),
]   