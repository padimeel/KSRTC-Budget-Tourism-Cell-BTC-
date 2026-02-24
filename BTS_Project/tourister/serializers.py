from rest_framework import serializers
from django.contrib.auth import get_user_model
<<<<<<< HEAD
from django.db import transaction
=======
>>>>>>> main
from .models import User, RateReview, Package_Booking, Package_Details,RoomBooking
from django.db.models import F

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
<<<<<<< HEAD
            package = Package_Details.objects.select_related('bus').get(id=package_id)
=======
            # We use select_for_update() to prevent race conditions during seat booking
            package = Package_Details.objects.select_for_update().select_related('bus').get(id=package_id)
>>>>>>> main
        except Package_Details.DoesNotExist:
            raise serializers.ValidationError({"package_id": "Package does not exist"})

        if not package.bus:
            raise serializers.ValidationError({"error": "No bus assigned to this package yet."})

        adults = data.get("adults", 0)
        children = data.get("children", 0)
        total_passengers = adults + children

        if total_passengers <= 0:
            raise serializers.ValidationError({"error": "At least one passenger is required."})

        if package.bus.total_seats < total_passengers:
            raise serializers.ValidationError({
                "error": f"Not enough seats. Available: {package.bus.total_seats}"
            })

<<<<<<< HEAD
        data['package_obj'] = package
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        package = validated_data.pop('package_obj')
        if "package_id" in validated_data:
            validated_data.pop("package_id")
        
        adults = validated_data.get("adults", 0)
        children = validated_data.get("children", 0)
        total_passengers = adults + children

        validated_data["total_price"] = (
            adults * package.price + (children * package.price * 0.5)
        )

        bus = package.bus
        bus.total_seats = F('total_seats') - total_passengers
        bus.save(update_fields=['total_seats'])

        return Package_Booking.objects.create(
            user=user,
            package=package,
            **validated_data
        )
=======
        # Pass the package object to the create method
        data['package_obj'] = package
        data['total_passengers'] = total_passengers
        return data

    def create(self, validated_data):
        package = validated_data.pop('package_obj')
        total_passengers = validated_data.pop('total_passengers')
        user = self.context['request'].user

        # 1. Price Calculation (Package Price * Number of People)
        calculated_price = package.price * total_passengers

        # 2. Decrease Seats in Bus model
        bus = package.bus
        bus.total_seats -= total_passengers
        bus.save()

        # 3. Create Booking Record
        booking = Package_Booking.objects.create(
            user=user,
            package=package,
            total_price=calculated_price,
            **validated_data
        )
        return booking
    
>>>>>>> main
        
        
        
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