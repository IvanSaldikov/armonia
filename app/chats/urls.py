from django.urls import path

from chats import views

urlpatterns = [
    path("room/<str:slug>/", views.index, name='chat'),
    path("join/<str:slug>/", views.room_get_or_create, name='room-get-or-create'),
    ]
