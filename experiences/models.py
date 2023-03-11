from django.db import models
from common.models import CommonModel
import datetime


class Experience(CommonModel):

    """Experience Model Definition"""

    country = models.CharField(
        max_length=50,
        default="한국",
    )
    city = models.CharField(
        max_length=80,
        default="서울",
    )
    name = models.CharField(
        max_length=250,
    )
    host = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    price = models.PositiveIntegerField()
    address = models.CharField(
        max_length=250,
    )
    start = models.TimeField()
    end = models.TimeField()
    description = models.TextField()
    perks = models.ManyToManyField(
        "experiences.Perk",
        related_name="experiences",
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="experiences",
    )

    def hour(experience):
        start = experience.start
        end = experience.end
        datetime_start = datetime.datetime.combine(
            datetime.date.today(),
            start,
        )
        datetime_end = datetime.datetime.combine(
            datetime.date.today(),
            end,
        )
        datetime_diff = datetime_end - datetime_start
        datetime_diff_in_hour = datetime_diff.total_seconds() / 3600
        return f"{datetime_diff_in_hour} 시간"

    def rating(experience):
        reviews = experience.reviews.all().values("rating")
        reviews_count = reviews.count()
        if reviews_count == 0:
            return 0
        else:
            total_rating = 0
            for review in reviews:
                total_rating += review["rating"]
            rating_average = round(total_rating / reviews_count)
            return rating_average

    def __str__(self) -> str:
        return self.name


class Perk(CommonModel):

    """What is included on an Experience"""

    name = models.CharField(
        max_length=100,
    )
    details = models.CharField(
        max_length=250,
        blank=True,
        null=True,
    )
    explanation = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.name
