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



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
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
# def send_invite(request):
#     form = InviteForm()

#     if request.method == "POST":
#         form = InviteForm(request.POST)

#         if form.is_valid():
#             username = form.cleaned_data["username"]

#             try:
#                 receiver = User.objects.get(username=username)

#                 # உங்களுக்கே invite அனுப்ப முடியாது
#                 if receiver == request.user:
#                     messages.error(request, "You cannot invite yourself!")
#                     return redirect("send_invite")

#                 # ஏற்கனவே pending invite இருக்கிறதா?
#                 if Invite.objects.filter(
#                     sender=request.user,
#                     receiver=receiver,
#                     accepted=False
#                 ).exists():
#                     messages.warning(request, "Invite already sent!")
#                     return redirect("send_invite")

#                 # ஏற்கனவே couple ஆக connect ஆகியிருக்கிறாங்களா?
#                 if Couple.objects.filter(
#                     user1=request.user,
#                     user2=receiver
#                 ).exists() or Couple.objects.filter(
#                     user1=receiver,
#                     user2=request.user
#                 ).exists():
#                     messages.warning(request, "You are already connected ❤️")
#                     return redirect("send_invite")

#                 # புதிய invite create
#                 Invite.objects.create(
#                     sender=request.user,
#                     receiver=receiver
#                 )

#                 messages.success(
#                     request,
#                     "Invite sent successfully! ❤️"
#                 )

#                 return redirect("dashboard")

#             except User.DoesNotExist:
#                 messages.error(
#                     request,
#                     "User not found!"
#                 )

#     return render(request, "send_invite.html", {"form": form})

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

    if request.method == "POST":
        text = request.POST.get("message")

        if text:
            Message.objects.create(
                couple=couple,
                sender=request.user,
                text=text
            )

        return redirect("chat")

    Message.objects.filter(
        couple=couple
    ).exclude(
        sender=request.user
    ).update(
        seen=True
    )

    messages = Message.objects.filter(
        couple=couple
    ).order_by("created_at")

    partner = couple.user2 if couple.user1 == request.user else couple.user1

    status = UserStatus.objects.filter(user=partner).first()

    return render(
        request,
        "chat.html",
        {
            "messages": messages,
            "couple": couple,
            "partner": partner,
            "status": status,
        }
    )