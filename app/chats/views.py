from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render, reverse, redirect

from api_keys.utils import APIKeysUtils
from chats.models import Room
from chats.utils.room import RoomUtils
from problems.utils import ProblemManager
from users.models import User


@login_required
def index(request, slug: str):
    try:
        room = RoomUtils.get_user_room_by_slug(slug=slug,
                                               user_id=request.user.id
                                               )
    except Room.DoesNotExist:
        return HttpResponseNotFound()
    messages = RoomUtils.get_room_messages(room_id=room.id)
    return render(request,
                  'chats/room.html',
                  {"name": room.name,
                   "problem": room.problem,
                   "slug": room.slug,
                   "chat_messages": messages,
                   "api_key": APIKeysUtils.get_user_latest_api_key_obj(user=room.user),
                   }
                  )


@login_required
def room_get_or_create(request, slug: str):
    user: User = request.user
    problem = ProblemManager.get_problem_by_slug(slug=slug, user=request.user)
    if problem:
        room = RoomUtils.get_or_crate_user_room(user=user, problem=problem)
        messages = RoomUtils.get_room_messages(room_id=room.id)
        return render(request,
                      'chats/room.html',
                      {"name": room.name,
                       "problem": room.problem,
                       "slug": room.slug,
                       "chat_messages": messages,
                       "api_key": APIKeysUtils.get_user_latest_api_key_obj(user=user),
                       }
                      )
    return redirect(reverse('problems-list-private'))
