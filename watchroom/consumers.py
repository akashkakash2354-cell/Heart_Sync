import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class WatchConsumer(WebsocketConsumer):

    def connect(self):

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        self.room_group_name = f"watch_{self.room_id}"


        async_to_sync(
            self.channel_layer.group_add
        )(
            self.room_group_name,
            self.channel_name
        )


        self.accept()


        print(
            "WATCH CONNECTED:",
            self.room_group_name
        )


    def disconnect(self, close_code):

        async_to_sync(
            self.channel_layer.group_discard
        )(
            self.room_group_name,
            self.channel_name
        )


    def receive(self, text_data):

        data = json.loads(text_data)


        async_to_sync(
            self.channel_layer.group_send
        )(
            self.room_group_name,
            {
                "type": "watch_event",
                "data": data
            }
        )


    def watch_event(self, event):

        self.send(
            text_data=json.dumps(
                event["data"]
            )
        )