from django.urls import re_path
from . import consumers


websocket_urlpatterns = [

    # Chat
    re_path(
        r"ws/chat/(?P<couple_id>\w+)/$",
        consumers.ChatConsumer.as_asgi()
    ),


    # Watch Together
    re_path(
        r"ws/watch/(?P<room_id>\w+)/$",
        consumers.WatchConsumer.as_asgi()
    ),

]