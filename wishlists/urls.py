from django.urls import path
from .views import (
    Wishlists,
    WishlistDetail,
    WishlistRoomSwitch,
    WishlistExperienceSwitch,
)

urlpatterns = [
    path("", Wishlists.as_view()),
    path("<int:pk>", WishlistDetail.as_view()),
    path("<int:pk>/rooms/<int:room_pk>", WishlistRoomSwitch.as_view()),
    path(
        "<int:pk>/experiences/<int:experience_pk>",
        WishlistExperienceSwitch.as_view(),
    ),
]
