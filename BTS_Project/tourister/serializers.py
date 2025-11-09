from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Profile,RateReview

class SignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }


    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password'])
        )

        Profile.objects.create(user=user, phone_number=phone_number)
        return user

class RateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateReview
        fields = ['id', 'user', 'rating', 'review']
        read_only_fields = ['user']