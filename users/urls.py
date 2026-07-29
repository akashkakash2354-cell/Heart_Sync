from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("invite/",views.send_invite,
    name="send_invite"),
    path("pending-invites/", views.pending_invites, name="pending_invites"),
    path("accept-invite/<int:invite_id>/",
     views.accept_invite,name="accept_invite"),
    path("logout/",views.logout_view,name="logout"),
    path("chat/", views.chat, name="chat"),
    path("watch/", views.watch_room, name="watch_room"),
]