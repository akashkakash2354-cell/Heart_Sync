from django.db import models
from django.contrib.auth.models import User


class Couple(models.Model):
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="partner1"
    )

    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="partner2"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} ❤️ {self.user2.username}"
    
class Invite(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invites"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_invites"
    )

    accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} ➜ {self.receiver.username}"