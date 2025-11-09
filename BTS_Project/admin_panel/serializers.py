from rest_framework import serializers
from .models import Package_Details, DayWiseItinerary


class DayWiseItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DayWiseItinerary
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    itineraries = DayWiseItinerarySerializer(many=True, read_only=True)

    class Meta:
        model = Package_Details
        fields = '__all__'
