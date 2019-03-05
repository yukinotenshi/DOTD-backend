from random import choice
from middleware.auth import AuthMiddleware
from misc import generate_random_string
from core.util import *
from redis_model import Room, Player, Session


def get_room(room_id):
    room = Room(room_id)
    try:
        room.load()
    except:
        return respond_message("Room not found", 404)

    return respond_data(room.to_dict())


def create_room():
    session = load_session()

    room_data = {
        "room_id": generate_random_string(8),
        "owner": session.username,
        "chasing_team": [session.username],
        "hiding_team": [],
    }

    room = Room(room_data["room_id"], room_data)
    room.save()

    player_data = {
        "username": session.username,
        "team_id": "",
        "room_id": room_data["room_id"],
        "lat": 0.0,
        "lng": 0.0,
    }

    player = Player(session.username, player_data)
    player.save()

    return jsonify(room.to_dict())


def join_room():
    included, error = check_json_in_request(["room_id"])
    if not included:
        return error

    session = load_session()
    player = Player(session.username)
    player.load()

    if player.room_id != '':
        return respond_message("Already in another rooom")

    room = Room(request.json["room_id"])
    try:
        room.load()
    except:
        return respond_message("Room not found", 404)

    if session.username in room.chasing_team:
        return respond_message("Already in room", 500)

    player_data = {
        "username": session.username,
        "team_id": "",
        "room_id": room.room_id,
        "lat": 0.0,
        "lng": 0.0,
    }

    player = Player(session.username, player_data)
    player.save()
    room.chasing_team.append(session.username)
    room.save()

    return respond_data(room.to_dict())


def leave_room():
    session = load_session()
    player = Player(session.username)
    player.load()

    room = Room(player.room_id)
    player.room_id = ''
    try:
        room.load()
    except:
        return respond_message("Room not found", 404)

    if session.username == room.owner:
        room.delete()
        player.save()
        player_usernames = room.chasing_team + room.hiding_team
        for username in player_usernames:
            p = Player(username)
            p.load()
            p.room_id = ''
            p.save()

        return respond_message("Room deleted", 200)

    if session.username in room.chasing_team:
        room.chasing_team.remove(session.username)
        room.save()
        player.save()
        return respond_data(room.to_dict())

    if session.username in room.hiding_team:
        room.hiding_team.remove(session.username)
        room.save()
        player.save()
        return respond_data(room.to_dict())

    return respond_message("Not in room", 404)


routes = {
    "/create": ("POST", AuthMiddleware(create_room)),
    "/<room_id>": ("GET", AuthMiddleware(get_room)),
    "/join": ("POST", AuthMiddleware(join_room)),
    "/leave": ("POST", AuthMiddleware(leave_room)),
}
