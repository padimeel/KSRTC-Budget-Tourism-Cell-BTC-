from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import Package_Details, DayWiseItinerary
from depot_management.models import BusDetails, BusRoute  

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


class DayWiseItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DayWiseItinerary
        fields = '__all__'


class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = ['location', 'arrival_time', 'departure_time', 'description']


class BusDetailsSerializer(serializers.ModelSerializer):
    routes = BusRouteSerializer(many=True, read_only=True)

    class Meta:
        model = BusDetails
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    itineraries = DayWiseItinerarySerializer(many=True, read_only=True)
    
    bus = BusDetailsSerializer(read_only=True)

    class Meta:
        model = Package_Details
        fields = '__all__'
        
class HotelSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'location']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            location=validated_data.get('location', ''),
            role='Hotel'
        )
        return user