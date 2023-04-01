from django.utils import timezone
from rest_framework import serializers
from .models import Booking
from users.serializers import TinyUserSerializer
from rooms.serializers import RoomListSerializer


class CreateRoomBookingSerializer(serializers.ModelSerializer):

    check_in = serializers.DateField()
    check_out = serializers.DateField()

    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )

    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate(self, data):
        room = self.context.get("room")
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError(
                "Check in should be smaller than check out."
            )
        if Booking.objects.filter(
            room=room,
            check_in__lte=data["check_out"],
            check_out__gte=data["check_in"],
        ).exists():
            raise serializers.ValidationError(
                "Those of dates are already taken."
            )
        return data


class PublicBookingSerializer(serializers.ModelSerializer):

    user = serializers.CharField()
    room = serializers.CharField()

    class Meta:
        model = Booking
        fields = (
            "pk",
            "user",
            "room",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )


class CreateExperienceBookingSerializer(serializers.ModelSerializer):

    experience_time = serializers.DateTimeField()

    class Meta:
        model = Booking
        fields = [
            "experience_time",
            "guests",
        ]

    def validate_experience_time(self, value):
        experience = self.context["experience"]
        if value.time() != experience.start:
            raise serializers.ValidationError(
                "Experience time have to be same with the experience start of time"
            )
        if experience.bookings.filter(experience_time=value).exists():
            raise serializers.ValidationError(
                "that experience is already taken"
            )
        return value
