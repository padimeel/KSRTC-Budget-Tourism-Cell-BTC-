from rest_framework import serializers
from .models import Transaction
from tourister.models import Package_Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package_Booking
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'