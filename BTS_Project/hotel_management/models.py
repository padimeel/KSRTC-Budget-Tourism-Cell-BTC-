# from django.contrib.auth.models import User
# from django.db import models

# class HotelProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     hotel_name = models.CharField(max_length=150)
#     city = models.CharField(max_length=100)
#     role = models.CharField(max_length=20, default='Hotel Management', editable=False)

#     def __str__(self):
#         return f"{self.username} - {self.hotel_name} ({self.city})"
