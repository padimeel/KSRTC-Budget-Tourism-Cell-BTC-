from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings

# உங்கள் App பெயர்களில் இருந்து மாடல்களை இறக்குமதி செய்யவும்
from .models import Package_Details, DayWiseItinerary
from depot_management.models import BusDetails, BusRoute  # BusRoute-ஐயும் இங்கே சேர்க்கவும்

User = get_user_model()

class DepotSignupSerializer(serializers.ModelSerializer):
    depot_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'depot_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        depot_name = validated_data.pop('depot_name')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            depot_name=depot_name,
            role="depot_manager"
        )
        return user

# 1. DayWiseItinerary Serializer (Package-க்கு தேவை)
class DayWiseItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DayWiseItinerary
        fields = '__all__'

# 2. BusRoute Serializer (BusDetails-க்கு தேவை)
class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = ['location', 'arrival_time', 'departure_time', 'description']

# 3. BusDetails Serializer (இதில் 'routes' இணைக்கப்பட்டுள்ளது)
class BusDetailsSerializer(serializers.ModelSerializer):
    # 'routes' என்பது BusRoute மாடலில் உள்ள related_name="routes"
    routes = BusRouteSerializer(many=True, read_only=True)

    class Meta:
        model = BusDetails
        fields = '__all__'

# 4. Package Serializer (இதில் 'itineraries' மற்றும் 'bus' இணைக்கப்பட்டுள்ளது)
class PackageSerializer(serializers.ModelSerializer):
    itineraries = DayWiseItinerarySerializer(many=True, read_only=True)
    
    # 'bus' என்பது BusDetails மாடலில் உள்ள related_name="bus"
    # OneToOneField என்பதால் many=True போடக்கூடாது
    bus = BusDetailsSerializer(read_only=True)

    class Meta:
        model = Package_Details
        fields = '__all__'