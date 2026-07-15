from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from .forms import InviteForm
from .models import Invite

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


def dashboard(request):
    return render(request, "dashboard.html")

def send_invite(request):
    form = InviteForm()

    if request.method == "POST":
        form = InviteForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]

            try:
                receiver = User.objects.get(username=username)

                Invite.objects.create(
                    sender=request.user,
                    receiver=receiver
                )

                messages.success(request, "Invite sent successfully!")

            except User.DoesNotExist:
                messages.error(request, "User not found!")

    return render(request, "send_invite.html", {"form": form})