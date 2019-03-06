from math import sqrt
from random import choice
from middleware.auth import AuthMiddleware
from misc import generate_random_string
from core.util import *
from redis_model import Room, Player, Game


def start_game():
    session = load_session()
    player = Player(session.username)
    player.load()

    room = Room(player.room_id)
    try:
        room.load()
    except:
        return respond_message("Room not found", 404)

    if room.owner != session.username:
        return respond_message("You are not the room owner", 400)

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

    game = Game(room.room_id)
    game.room = room
    game.load_players()
    game.save()

    return respond_data(game.to_dict())


def submit_location():
    lat = request.json.get("lat")
    lng = request.json.get("lng")

    session = load_session()

    p = Player(session.username)
    p.load()
    p.lat = lat
    p.lng = lng
    p.save()

    return respond_data(p.to_dict())


def get_status(game_id):
    session = load_session()
    game = Game(game_id)
    game.load()
    if session.username not in [p.username for p in game.players]:
        return respond_message("You are not in game : {}".format(game_id), 403)

    return respond_data(game.to_dict())


def get_intensity():
    session = load_session()
    player = Player(session.username)
    player.load()

    try:
        game = Game(player.room_id)
        game.load()
    except:
        return respond_data("Not in game", 404)

    score = 0
    nearest_player = None
    for p in game.players:
        if not p.alive:
            continue

        if p.username == session.username:
            continue

        if p.team_id == player.team_id:
            continue

        x_dist = p.lat - player.lat
        y_dist = p.lng - player.lng
        # 1 degree lat/lng is approx 111km
        distance = sqrt(x_dist ** 2 + y_dist ** 2) * 111000
        if distance < 3 and score < 1:
            nearest_player = p
            score = 1
        elif distance < 5 and score < 0.8:
            nearest_player = p
            score = 0.8
        elif distance < 7 and score < 0.5:
            nearest_player = p
            score = 0.5
        elif distance < 10 and score < 0.2:
            nearest_player = p
            score = 0.2
        else:
            continue

    data = {"intensity": score}
    if score == 1:
        data["player"] = nearest_player.to_dict()

    return respond_data(data)


def catch():
    session = load_session()
    player = Player(session.username)
    player.load()

    try:
        game = Game(player.room_id)
        game.load()
    except:
        return respond_data("Not in game", 404)

    for p in game.players:
        if not p.alive:
            continue

        if p.username == session.username:
            continue

        if p.team_id == player.team_id:
            continue

        x_dist = p.lat - player.lat
        y_dist = p.lng - player.lng
        # 1 degree lat/lng is approx 111km
        distance = sqrt(x_dist ** 2 + y_dist ** 2) * 111000
        if distance > 3:
            continue

        p.alive = False
        p.save()

        return respond_data(p.to_dict())

    return respond_message("No catchable player in radius", 404)


def get_player():
    session = load_session()
    player = Player(session.username)
    player.load()

    return respond_data(player.to_dict())


def end_game():
    session = load_session()
    player = Player(session.username)
    player.load()

    game = Game(player.room_id)
    game.load()

    for p in game.room.hiding_team:
        player = Player(p)
        player.load()
        if player.alive:
            return respond_data({"winner": player.team_id})

    player = Player(game.room.chasing_team[0])
    player.load()

    return respond_data({"winner": player.team_id})


routes = {
    "/location": ("POST", AuthMiddleware(submit_location)),
    "/start": ("POST", AuthMiddleware(start_game)),
    "/<game_id>": ("GET", AuthMiddleware(get_status)),
    "/intensity": ("GET", AuthMiddleware(get_intensity)),
    "/catch": ("POST", AuthMiddleware(catch)),
    "/player": ("GET", AuthMiddleware(get_player)),
    "/end": ("GET", AuthMiddleware(end_game)),
}
