import datetime
import pytz
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from .models import Perk, Experience
from . import serializers
from categories.models import Category
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer, VideoSerializer
from bookings.serializers import (
    PublicBookingSerializer,
    CreateExperienceBookingSerializer,
)
from bookings.models import Booking


class Perks(APIView):
    def get(self, request):
        all_perks = Perk.objects.all()
        serializer = serializers.PerkSerializer(all_perks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.PerkSerializer(request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(serializers.PerkSerializer(perk).data)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):
    def get_object(self, pk):
        try:
            return Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(perk)
        return Response(serializer.data)

    def put(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(
            perk,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_perk = serializer.save()
            return Response(serializers.PerkSerializer(updated_perk).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response(status=status.HTTP_404_NOT_FOUND)


class Experiences(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        experiences = Experience.objects.all()
        serializer = serializers.ExperienceListSerializer(
            experiences,
            many=True,
            context={
                "request": request,
            },
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.ExperienceDetailSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError("Category kind have to be an experience")
            except Category.DoesNotExist:
                raise NotFound
            try:
                with transaction.atomic():
                    experience = serializer.save(
                        host=request.user,
                        category=category,
                    )
                    perks = request.data.get("perks")
                    for perk_pk in perks:
                        perk = Perk.objects.get(pk=perk_pk)
                        experience.perks.add(perk)
                    serializer = serializers.ExperienceDetailSerializer(
                        experience,
                        context={"request": request},
                    )
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Perk not found")
        else:
            return Response(serializer.errors)


class ExperienceDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        serializer = serializers.ExperienceDetailSerializer(
            experience,
            context={
                "request": request,
            },
        )
        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        serializer = serializers.ExperienceDetailSerializer(
            experience,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.ROOMS:
                        raise ParseError(
                            "The category should have kind of experience"
                        )
                    experience = serializer.save(category=category)
                except Category.DoesNotExist:
                    raise NotFound
            else:
                experience = serializer.save()

            perks = request.data.get("perks")
            if perks:
                experience.perks.clear()
                for perk_pk in perks:
                    try:
                        perk = Perk.objects.get(pk=perk_pk)
                        experience.perks.add(perk)
                    except Perk.DoesNotExist:
                        raise NotFound("Perks not updated correctly")

            serializer = serializers.ExperienceDetailSerializer(
                experience,
                context={"request": request},
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        experience = self.get_object(pk=pk)
        if experience.host != request.user:
            raise PermissionDenied
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExperiencePerks(APIView):
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):

        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        experience = self.get_object(pk)
        perks = experience.perks.all()[start:end]
        serializer = serializers.PerkSerializer(
            perks,
            many=True,
        )
        return Response(serializer.data)


class ExperienceReviews(APIView):
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        experience = self.get_object(pk)
        reviews = experience.reviews.all()[start:end]
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ExperiencePhotos(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(experience=experience)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceVideo(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def put(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save(experience=experience)
            serializer = VideoSerializer(video)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceBookings(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        now = timezone.localtime(timezone.now())
        try:
            month = int(request.query_params.get("month", now.month))
            year = int(request.query_params.get("year", now.year))
            if year < now.year:
                year = now.year
                month = now.month
            if (year == now.year) and (month < now.month):
                month = now.month
        except:
            month = now.month
            year = now.year
        start = datetime.datetime(year, month, 1, tzinfo=pytz.UTC)
        if month == 12:
            end = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
        else:
            end = datetime.datetime(year, month + 1, 1, tzinfo=pytz.UTC)

        experience = self.get_object(pk)
        bookings = experience.bookings.filter(
            kind=Booking.BookingKindChoices.EXPERIENCE,
            experience_time__gte=start,
            experience_time__lt=end,
        )
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        experience = self.get_object(pk)
        serializer = CreateExperienceBookingSerializer(
            data=request.data,
            context={"experience": experience},
        )
        if serializer.is_valid():
            booking = serializer.save(
                experience=experience,
                user=request.user,
                kind=Booking.BookingKindChoices.EXPERIENCE,
            )
            serializer = CreateExperienceBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
