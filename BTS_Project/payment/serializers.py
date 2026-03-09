from rest_framework import serializers
from .models import Transaction
from tourister.models import Package_Booking
from admin_panel.models import Package_Details
from django.db.models import F
from django.db import transaction
        


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer to handle Package Bookings with seat validation 
    and atomic seat count updates.
    """
    user = serializers.StringRelatedField(read_only=True)
    package = serializers.StringRelatedField(read_only=True)
    bus = serializers.StringRelatedField(source='package.bus', read_only=True)
    package_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Package_Booking
        fields = [
            'id', 'user', 'package', 'bus',
            'adults', 'children', 'boarding_point',
            'phone_number', 'total_price', 'booking_date',
            'package_id'
        ]
        read_only_fields = ['total_price', 'booking_date']

    def validate(self, data):
        package_id = data.get("package_id")
        
        try:
            # select_for_update() locks the row to prevent other processes 
            # from modifying the package/bus during this transaction.
            package = Package_Details.objects.select_for_update().select_related('bus').get(id=package_id)
        except Package_Details.DoesNotExist:
            raise serializers.ValidationError({"package_id": "The specified package does not exist."})

        # Ensure a bus is assigned to the package
        if not package.bus:
            raise serializers.ValidationError({"error": "No bus has been assigned to this package yet."})

        adults = data.get("adults", 0)
        children = data.get("children", 0)
        total_passengers = adults + children

        # Passenger count validation
        if total_passengers <= 0:
            raise serializers.ValidationError({"error": "At least one passenger (adult or child) is required."})

        # Seat availability validation
        if package.bus.total_seats < total_passengers:
            raise serializers.ValidationError({
                "error": f"Not enough seats available. Remaining: {package.bus.total_seats}"
            })

        # Pass objects to the create method via validated_data
        data['package_obj'] = package
        data['total_passengers'] = total_passengers
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Calculates price, updates bus seats using F expressions, 
        and creates the booking record.
        """
        package = validated_data.pop('package_obj')
        total_passengers = validated_data.pop('total_passengers')
        user = self.context['request'].user

        # Business Logic: Calculate total price
        calculated_price = package.price * total_passengers

        # Atomic seat update to prevent race conditions
        bus = package.bus
        bus.total_seats = F('total_seats') - total_passengers
        bus.save()

        # Create the booking instance
        booking = Package_Booking.objects.create(
            user=user,
            package=package,
            total_price=calculated_price,
            **validated_data
        )
        
        return booking

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'