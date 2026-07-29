from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Invite, Couple, UserStatus
from .forms import InviteForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from .models import Message, UserStatus
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Message
from .models import WatchRoom, Couple
import re
import urllib.parse



def register(request):
    if request.method == "POST":

        
        messages.success(request, "Account created successfully!")
        return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

    return render(request, "login.html")

@login_required
def dashboard(request):

    couple = Couple.objects.filter(
        user1=request.user
    ).first()

    if not couple:
        couple = Couple.objects.filter(
            user2=request.user
        ).first()

    return render(
        request,
        "dashboard.html",
        {"couple": couple}
    )

@login_required
def send_invite(request):
    form = InviteForm()

    if request.method == "POST":
        form = InviteForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]

            try:
                receiver = User.objects.get(username=username)

                # Self invite
                if receiver == request.user:
                    messages.error(request, "You cannot invite yourself!")
                    return redirect("send_invite")

                # Pending invite already exists
                if Invite.objects.filter(
                    sender=request.user,
                    receiver=receiver
                ).exists():
                    messages.warning(request, "Invite already sent!")
                    return redirect("send_invite")

                # Already connected
                if Couple.objects.filter(
                    user1=request.user,
                    user2=receiver
                ).exists() or Couple.objects.filter(
                    user1=receiver,
                    user2=request.user
                ).exists():
                    messages.warning(request, "You are already connected ❤️")
                    return redirect("dashboard")

                Invite.objects.create(
                    sender=request.user,
                    receiver=receiver
                )

                messages.success(request, "Invite sent successfully ❤️")
                return redirect("dashboard")

            except User.DoesNotExist:
                messages.error(request, "User not found!")

    return render(request, "send_invite.html", {"form": form})


@login_required
def pending_invites(request):
    print("LOGIN USER:", request.user)

    invites = Invite.objects.filter(
        receiver=request.user,
        accepted=False
    )

    print("INVITES:", invites)

    return render(
        request,
        "pending_invites.html",
        {"invites": invites}
    )

@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(Invite, id=invite_id)

    if not Couple.objects.filter(
        user1=invite.sender,
        user2=invite.receiver
    ).exists():

        Couple.objects.create(
            user1=invite.sender,
            user2=invite.receiver
        )

    invite.delete()

    messages.success(request, "You are connected ❤️")

    return redirect("dashboard")

def logout_view(request):
    logout(request)
    return redirect("login")
@login_required
def chat(request):

    couple = Couple.objects.filter(user1=request.user).first()

    if not couple:
        couple = Couple.objects.filter(user2=request.user).first()

    if not couple:
        return redirect("dashboard")


    # MARK MESSAGE SEEN
    Message.objects.filter(
        couple=couple
    ).exclude(
        sender=request.user
    ).update(
        seen=True
    )


    channel_layer = get_channel_layer()


    last_message = Message.objects.filter(
        couple=couple
    ).exclude(
        sender=request.user
    ).last()


    print("🔥 LAST MESSAGE:", last_message)


    if last_message:

        print("🔥 SENDING SEEN:", last_message.id)

        async_to_sync(channel_layer.group_send)(
            f"chat_{couple.id}",
            {
                "type": "seen_message",
                "message_id": last_message.id,
            }
        )


    chat_messages = Message.objects.filter(
        couple=couple
    ).order_by("created_at")


    partner = (
        couple.user2
        if couple.user1 == request.user
        else couple.user1
    )


    status = UserStatus.objects.filter(
        user=partner
    ).first()


    return render(
        request,
        "chat.html",
        {
            "messages": chat_messages,
            "couple": couple,
            "partner": partner,
            "status": status,
        }
    )
    
@login_required
def watch_room(request):

    couple = Couple.objects.filter(
        user1=request.user
    ).first()

    if not couple:
        couple = Couple.objects.filter(
            user2=request.user
        ).first()

    room, created = WatchRoom.objects.get_or_create(
        couple=couple
    )

    if request.method == "POST":
        room.youtube_url = request.POST.get("youtube_url")
        room.save()

    video_id = None

    if room.youtube_url:
        match = re.search(
    r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})",
    room.youtube_url
)

        if match:
            video_id = match.group(1)

    print("VIDEO ID:", video_id)

    search_url = None

    if request.GET.get("search"):
        query = request.GET.get("search")

        search_url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(query)
        )

    return render(
        request,
        "watch.html",
        {
            "room": room,
            "couple": couple,
            "video_id": video_id,
            "search_url": search_url,
        }
    )