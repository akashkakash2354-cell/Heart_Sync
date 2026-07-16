import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .models import Couple, Message, UserStatus



class ChatConsumer(WebsocketConsumer):

     def connect(self):
        self.couple_id = self.scope["url_route"]["kwargs"]["couple_id"]
        self.room_group_name = f"chat_{self.couple_id}"

        print("ROOM:", self.room_group_name)
        print("CHANNEL:", self.channel_name)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        UserStatus.objects.update_or_create(
            user=self.scope["user"],
            defaults={"is_online": True}
        )
        self.accept()

     def disconnect(self, close_code):
        print("❌ DISCONNECTED:", close_code)
        UserStatus.objects.update_or_create(
            user=self.scope["user"],
            defaults={"is_online": False}
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


     def receive(self, text_data):
        print("🔥 RECEIVE CALLED")
        print("DATA:", text_data)

        data = json.loads(text_data)

        if data.get("typing"):
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "typing_message",
                    "sender": self.scope["user"].username,
                }
            )
            return

        user = self.scope["user"]

        print("SENDING TO GROUP:", self.room_group_name)

        couple = Couple.objects.get(id=self.couple_id)

        Message.objects.create(
            couple=couple,
            sender=user,
            text=data["message"]
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": data["message"],
                "sender": user.username,
                "seen": False,
            }
        )

     def chat_message(self, event):
        print("🔥 CHAT MESSAGE:", event)

        self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "seen": event.get("seen", False),
                }
            )
        )
     def typing_message(self, event):
        self.send(
            text_data=json.dumps(
                {
                    "typing": True,
                    "sender": event["sender"],
                }
            )
        )