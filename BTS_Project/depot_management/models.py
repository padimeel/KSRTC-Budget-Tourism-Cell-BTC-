from django.contrib.auth.models import User
from django.db import models
from admin_panel.models import Package_Details

class BusDetails(models.Model):

    BUS_TYPE_CHOICES = [
        ('AC', 'AC Bus'),
        ('NON-AC', 'Non-AC Bus'),
        ('SLEEPER', 'Sleeper Bus'),
        ('SEMI-SLEEPER', 'Semi Sleeper Bus'),
        ('VOLVO', 'Volvo Bus'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buses", null=True)
    package = models.ForeignKey(Package_Details, on_delete=models.CASCADE, related_name="buses", null=True)
    
    

    bus_name = models.CharField(max_length=100, default="KSRTC BUS", editable=False)
    bus_number = models.CharField(max_length=50)
    route_name = models.CharField(max_length=100)
    total_seats = models.IntegerField()
    bus_type = models.CharField(max_length=50, choices=BUS_TYPE_CHOICES)

    def __str__(self):
        return f"{self.bus_name} - {self.bus_number}"


class BusRoute(models.Model):
    bus = models.ForeignKey(BusDetails, on_delete=models.CASCADE, related_name="routes", null=True)
    
    location = models.CharField(max_length=100)
    arrival_time = models.TimeField()
    departure_time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bus.bus_number} → {self.location}"
# Fetch specific packages based on Admin allocation using the Package_details API.# models.py
class DepotManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    depot_name = models.CharField(max_length=100)
class Package(models.Model):
    package_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
class PackageAllocation(models.Model):
    depot_manager = models.ForeignKey(DepotManager, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    # msg page
class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
