from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, RateReview, Package_Booking, Package_Details,RoomBooking
from django.db.models import F
from django.db import transaction

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number")
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=phone_number,
            role="Tourister"
        )
        return user

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
    
        
        
        
class RateReviewSerializer(serializers.ModelSerializer):
    user = SignupSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RateReview
        fields = ['user', 'rating', 'review', 'user_id']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User does not exist."})
        
        return RateReview.objects.create(user=user, **validated_data)
    
    
class RoomBookingSerializer(serializers.ModelSerializer):
    hotel_name = serializers.ReadOnlyField(source='room.hotel.hotel_name')
    room_number = serializers.ReadOnlyField(source='room.room_number')
    room_type = serializers.ReadOnlyField(source='room.room_type')
    price_per_night = serializers.ReadOnlyField(source='room.price')

    class Meta:
        model = RoomBooking
        fields = [
            'id', 'hotel_name', 'room_number', 'room_type', 'price_per_night',
            'guest_name', 'check_in_date', 'check_out_date', 
            'phone_number', 'adults', 'children', 'total_price'
        ]
        read_only_fields = ['id', 'user', 'room']