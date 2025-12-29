from django.urls import path
from .views import Login,BusAPI,RouteAPI,DepotDashboard,AssignPackage,DepotLogout,AddBus,UpdateBus

app_name='depot'

urlpatterns = [
    
    path('login/', Login.as_view(), name='login'),
    path('bus/', BusAPI.as_view()),          
    path('bus/<int:pk>/', BusAPI.as_view()),  
    path('route/', RouteAPI.as_view()),           
    path('route/<int:pk>/', RouteAPI.as_view()),
    path('depotdashboard/', DepotDashboard.as_view()),
    path('assignpackage/', AssignPackage.as_view(), name='assignpackage'),
    path('depotlogout/', DepotLogout.as_view(), name='depotlogout'),
    path('addbus/<int:pk>/', AddBus.as_view(), name='addbus'),
    path('updatebus/<int:pk>/', UpdateBus.as_view(), name='updatebus')
]
