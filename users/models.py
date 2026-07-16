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
    

class Message(models.Model):
    couple = models.ForeignKey(
        Couple,
        on_delete=models.CASCADE
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:20]}"


class SpecialDate(models.Model):
    couple = models.OneToOneField(Couple, on_delete=models.CASCADE)
    anniversary = models.DateField()
    birthday_user1 = models.DateField()
    birthday_user2 = models.DateField()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)