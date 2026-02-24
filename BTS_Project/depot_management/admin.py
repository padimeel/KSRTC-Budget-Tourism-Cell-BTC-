from django.contrib import admin
from .models import BusDetails, BusRoute

class BusRouteInline(admin.TabularInline):
    model = BusRoute
    extra = 3  
    fields = ['location', 'arrival_time', 'departure_time', 'description']

@admin.register(BusDetails)
class BusDetailsAdmin(admin.ModelAdmin):
    list_display = ['bus_name', 'bus_number', 'route_name', 'package', 'bus_type']
    inlines = [BusRouteInline]  

@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['location', 'bus', 'arrival_time', 'departure_time']
    list_filter = ['bus'] 