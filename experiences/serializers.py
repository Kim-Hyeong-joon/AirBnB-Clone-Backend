from rest_framework import serializers
import datetime
from .models import Perk, Experience
from medias.serializers import PhotoSerializer, VideoSerializer
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer


class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perk
        fields = (
            "id",
            "name",
            "details",
            "explanation",
        )


class ExperienceListSerializer(serializers.ModelSerializer):

    photos = PhotoSerializer(read_only=True, many=True)
    video = VideoSerializer(read_only=True)
    hour = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = (
            "pk",
            "city",
            "name",
            "price",
            "hour",
            "rating",
            "photos",
            "video",
            "is_owner",
            "is_liked",
        )

    def get_rating(self, experience):
        return experience.rating()

    def get_hour(self, experience):
        return experience.hour()

    def get_is_owner(self, experience):
        request = self.context["request"]
        return request.user == experience.host

    def get_is_liked(self, experience):
        try:
            request = self.context["request"]
            return experience.wishlists.filter(
                experiences__pk=experience.pk,
                user=request.user,
            ).exists()
        except:
            return False


class ExperienceDetailSerializer(serializers.ModelSerializer):

    host = TinyUserSerializer(
        read_only=True,
    )
    category = CategorySerializer(
        read_only=True,
    )
    perks = PerkSerializer(
        read_only=True,
        many=True,
    )
    photos = PhotoSerializer(
        read_only=True,
        many=True,
    )
    video = VideoSerializer(
        read_only=True,
    )
    hour = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = (
            "id",
            "host",
            "category",
            "perks",
            "country",
            "city",
            "name",
            "price",
            "start",
            "end",
            "description",
            "address",
            "hour",
            "rating",
            "photos",
            "video",
            "is_owner",
            "is_liked",
        )
        # fields = "__all__"

    def get_rating(self, experience):
        return experience.rating()

    def get_hour(self, experience):
        return experience.hour()

    def get_is_owner(self, experience):
        request = self.context["request"]
        return request.user == experience.host

    def get_is_liked(self, experience):
        try:
            request = self.context["request"]
            return experience.wishlists.filter(
                experiences__pk=experience.pk,
                user=request.user,
            ).exists()
        except:
            return False
