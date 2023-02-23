from django.shortcuts import render
from django.http import HttpResponse
from .models import Room

# Create your views here.
def see_all_rooms(request):
    rooms = Room.objects.all()
    return render(
        request,
        "all_rooms.html",
        {
            "rooms": rooms,
            "title": "Hello! this title comes from Django!",
        },
    )


def see_one_room(request, room_pk):
    room = Room.objects.get(pk=room_pk)
    return render(
        request,
        "room_detail.html",
        {
            "room": room,
        },
    )
