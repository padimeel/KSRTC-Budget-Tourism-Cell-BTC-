from rest_framework import serializers
from .models import BusDetails, BusRoute
from .models import Message
class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = ['id', 'bus', 'location', 'arrival_time', 'departure_time', 'description']


class BusDetailsSerializer(serializers.ModelSerializer):
    routes = BusRouteSerializer(many=True, read_only=True)

    class Meta:
        model = BusDetails
        fields = [
            'id',
            'user',
            'package',
            'bus_name',
            'bus_number',
            'route_name',
            'total_seats',
            'bus_type',
            'routes'
        ]
# memoryview
from rest_framework import serializers
from .models import Package

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"

# msg
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
