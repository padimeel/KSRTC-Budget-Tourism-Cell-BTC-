from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from admin_panel.models import Package_Details
from depot_management.models import BusDetails


class User(AbstractUser):
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    depot_name = models.CharField(max_length=100, blank=True, null=True)

    ROLE_CHOICES = [
        ("Tourister", "Tourister"),
        ("Depot Manager", "Depot Manager"),
    
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Tourister")

    def __str__(self):
        return self.username


class RateReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}"


class Package_Booking(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    package = models.ForeignKey(Package_Details, on_delete=models.CASCADE)

    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)

    boarding_point = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    total_price = models.PositiveIntegerField(default=0)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username}"
