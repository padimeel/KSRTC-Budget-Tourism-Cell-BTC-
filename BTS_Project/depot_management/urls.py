from django.urls import path
from .views import *
app_name='depot'

urlpatterns = [
    
    path('login/', Login.as_view(), name='login'),
    path('bus/', BusAPI.as_view()),          
    path('bus/<int:pk>/', BusAPI.as_view()),  
    path('route/', RouteAPI.as_view()),           
    path('route/<int:pk>/', RouteAPI.as_view()),
    # path('depotdashboard/', DepotDashboard.as_view()),
    path('assignpackage/', AssignPackage.as_view(), name='assignpackage'),
    path('depotlogout/', DepotLogout.as_view(), name='depotlogout'),
    # path('addbus/<int:pk>/', AddBus.as_view(), name='addbus'),
    path('updatebus/<int:pk>/', UpdateBus.as_view(), name='updatebus'),
    
    
    # Depot Routes
    path('addbus-template/', AddBusTemplate.as_view(), name='addbus_template'),
    path('assignpackage-template/', AssignPackageTemplate.as_view(), name='assignpackage_template'),
    path('depotdashboard-template/', DepotDashboardTemplate.as_view(), name='depotdashboard_template'),
    path('depotlogin-template/', DepotLoginTemplate.as_view(), name='depotlogin_template'),
    path('updatebus-template/', UpdateBusTemplate.as_view(), name='updatebus_template'),
    path('updatebus-template/<int:pk>/', UpdateBusTemplate.as_view(), name='updatebus_template'),
    path('addbus-template/<int:pk>/', AddBusTemplate.as_view(), name='addbus_template'),
    
    
]
