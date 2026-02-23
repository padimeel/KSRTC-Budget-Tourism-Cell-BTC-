from rest_framework import serializers
from .models import HotelProfile,Room

class HotelProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelProfile
        fields = '__all__'
        read_only_fields = ['user']
        
class RoomSerializer(serializers.ModelSerializer):
    hotel = HotelProfileSerializer(read_only=True) 

    class Meta:
        model = Room
        fields = ['id', 'room_type', 'room_number', 'price', 'is_available', 'hotel']
        
        
