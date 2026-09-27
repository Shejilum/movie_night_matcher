from django.urls import re_path  # pyright: ignore[reportMissingModuleSource]
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/room/(?P<room_code>\w+)/$", consumers.RoomConsumer.as_asgi()),
]