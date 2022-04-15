from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date

from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):
    flight = serializers.SlugRelatedField(
        read_only=True,
        slug_field='destination'
     )

    class Meta:
        model = Booking
        fields = ['flight', 'date', 'id']


class BookingDetailsSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['total', 'flight', 'date', 'passengers', 'id']
    
    def get_total(self, obj):
        passengers = obj.passengers
        flight_price = obj.flight.price
        return passengers*flight_price


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username, first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data

class UserSerialzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerialzer()
    past_bookings = serializers.SerializerMethodField()
    tier = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'miles', 'past_bookings', 'tier']

    def get_past_bookings(self, obj):
        booking = Booking.objects.filter(user=obj.user, date__lt=date.today())
        return BookingSerializer(booking, many=True).data

    def get_tier(self, obj):
        miles = obj.miles
        if 0 <= miles <= 9999:
            tier = 'Blue'
            return tier
        elif 10000 <= miles <= 59999:
            tier = 'Silver'
            return tier
        elif 60000 <= miles <= 99999:
            tier = 'Gold'
            return tier
        elif miles <= 100000:
            tier = 'Platinum'
            return tier
        else:
            print('Miles number invalid')


