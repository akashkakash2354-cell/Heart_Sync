import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .models import Couple, Message, UserStatus


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.couple_id = self.scope["url_route"]["kwargs"]["couple_id"]
        self.room_group_name = f"chat_{self.couple_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        user = self.scope["user"]

        UserStatus.objects.update_or_create(
            user=user,
            defaults={"is_online": True}
        )
        print("📤 Sending Online Status")
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "status_update",
                "status": "online",
                "username": user.username,
            }
        )
        print("✅ GROUP SEND SUCCESS")
        
    def disconnect(self, close_code):
        user = self.scope["user"]

        UserStatus.objects.update_or_create(
            user=user,
            defaults={"is_online": False}
        )
        
        print("📤 Sending offline Status") 

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "status_update",
                "status": "offline",
                "username": user.username,
            }
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("📤 Sending Offline Status")
        
        print("❌ DISCONNECTED:", user)

    def receive(self, text_data):
        user = self.scope["user"]
        couple = Couple.objects.get(id=self.couple_id)
        print("🔥 RECEIVE:", text_data)

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

        message = data.get("message")

        if not message:
            return

        user = self.scope["user"]
        couple = Couple.objects.get(id=self.couple_id)

        msg = Message.objects.create(
            couple=couple,
            sender=user,
            text=message
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg.text,
                "sender": user.username,
                "seen": msg.seen,
                "id": msg.id,
            }
        )
        msg.seen = True
        msg.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "seen_message",
                "message_id": msg.id,
            }
                )

        
    def chat_message(self, event):
        print("🔥 CHAT MESSAGE:", event)
        self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "seen": event["seen"],
            "id": event["id"],
        }))

    def typing_message(self, event):
        self.send(text_data=json.dumps({
            "typing": True,
            "sender": event["sender"],
        }))

    def status_update(self, event):
        
        print("🔥 STATUS UPDATE:", event)
        self.send(text_data=json.dumps({
            "status": event["status"],
            "username": event["username"],
        }))

    def seen_message(self, event):
        print("🔥 SEEN MESSAGE:", event)

        self.send(text_data=json.dumps({
        "seen": True,
        "message_id": event["message_id"],
    }))