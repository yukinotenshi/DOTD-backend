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
        return respond_error("Room not found", 404)

    return respond_data(room.to_dict())


def create_room():
    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_error("Session not found", 400)

    session = Session(access_token)
    session.load()

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

    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_error("Session not found", 400)

    session = Session(access_token)
    session.load()

    room = Room(request.json["room_id"])
    try:
        room.load()
    except:
        return respond_error("Room not found", 404)

    if session.username in room.chasing_team:
        return respond_error("Already in room", 500)

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


def start_room():
    included, error = check_json_in_request(["room_id"])
    if not included:
        return error

    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_error("Session not found", 400)

    session = Session(access_token)
    session.load()

    room = Room(request.json["room_id"])
    try:
        room.load()
    except:
        return respond_error("Room not found", 404)

    if room.owner != session.username:
        return respond_error("You are not the room owner", 400)

    chasing_team = []
    hiding_team = []
    player_count = len(room.chasing_team)

    for _ in range(player_count // 2):
        username = choice(room.chasing_team)
        player = Player(username)
        player.load()
        player.team_id = room.room_id + "hiding"
        player.save()
        hiding_team.append(username)

    for p in room.chasing_team:
        if p in hiding_team:
            continue
        player = Player(p)
        player.load()
        player.team_id = room.room_id + "chasing"
        player.save()
        chasing_team.append(p)

    room.chasing_team = chasing_team
    room.hiding_team = hiding_team
    room.save()

    return respond_data(room.to_dict())


def leave_room():
    included, error = check_json_in_request(["room_id"])
    if not included:
        return error

    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_error("Session not found", 400)

    session = Session(access_token)
    session.load()

    room = Room(request.json["room_id"])
    try:
        room.load()
    except:
        return respond_error("Room not found", 404)

    if session.username in room.chasing_team:
        room.chasing_team.remove(session.username)
        room.save()
        return respond_data(room.to_dict())

    if session.username in room.hiding_team:
        room.hiding_team.remove(session.username)
        room.save()
        return respond_data(room.to_dict())

    return respond_error("Not in room", 404)


routes = {
    "/create": ("POST", AuthMiddleware(create_room)),
    "/<room_id>": ("GET", AuthMiddleware(get_room)),
    "/join": ("POST", AuthMiddleware(join_room)),
    "/start": ("POST", AuthMiddleware(start_room)),
    "/leave": ("POST", AuthMiddleware(leave_room)),
}
