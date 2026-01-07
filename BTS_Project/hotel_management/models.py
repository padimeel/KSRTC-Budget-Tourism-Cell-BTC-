from django.db import models
from django.conf import settings

class HotelProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="hotel_profile"
    )
    hotel_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    city = models.CharField(max_length=100)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    map_location = models.URLField(blank=True, null=True)
    description = models.TextField()
    
    amenities = models.JSONField(default=list)
    hotel_banner_images = models.JSONField(default=list)
    room_images = models.JSONField(default=list)
    
    total_rooms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hotel_name
    
    
class Room(models.Model):
    ROOM_CATEGORIES = [
        ('Deluxe', 'Deluxe Room'),
        ('Standard', 'Standard Room')
    ]
    
    hotel = models.ForeignKey(HotelProfile, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=50, choices=ROOM_CATEGORIES)
    room_number = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_type} - {self.room_number}"