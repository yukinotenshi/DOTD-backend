from math import sqrt
from random import choice
from middleware.auth import AuthMiddleware
from core.util import *
from redis_model import Room, Player, Game
from skeleton.character import *


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
        player = choice(room.chasing_team)
        player = Player(player["username"])
        player.load()
        player.team_id = room.room_id + "hiding"
        player.character = choice(hiding_characters)
        player.save()
        hiding_team.append(player.username)

    for player in room.chasing_team:
        if player["username"] in hiding_team:
            continue
        player = Player(player["username"])
        player.load()
        player.character = choice(chasing_characters)
        player.team_id = room.room_id + "chasing"
        player.save()
        chasing_team.append(player.username)

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
        if distance < 5 and score < 1:
            nearest_player = p
            score = 1
        elif distance < 7 and score < 0.8:
            nearest_player = p
            score = 0.8
        elif distance < 9 and score < 0.5:
            nearest_player = p
            score = 0.5
        elif distance < 11 and score < 0.2:
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
        if distance > 5:
            continue

        p.alive = False
        player.exp += 50
        if player.exp // 100 > 0:
            player.level += player.exp // 100
            player.exp = player.exp % 100
        player.save()
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


def game_summary():
    session = load_session()
    player = Player(session.username)
    player.load()

    game = Game(player.room_id)
    game.load()

    time = request.json.get('time')
    if player.team_id[-4] == 'd':
        exp_diff = int(time / 6)
        player.level += exp_diff // 100
        player.exp = (exp_diff + player.exp) % 100
        player.save()
    else:
        user = User.get_or_none(User.username == session.username)
        exp_diff = (player.level - user.level) * 100 + player.exp - user.exp

    user = User.get_or_none(User.username == session.username)
    user.exp = player.exp
    user.level = player.level
    user.save()

    summary = {
        'exp_gain': exp_diff,
        'level_gain': exp_diff // 100,
        'exp': player.exp,
        'level': player.level
    }

    return respond_data(summary)


routes = {
    "/location": ("POST", AuthMiddleware(submit_location)),
    "/start": ("POST", AuthMiddleware(start_game)),
    "/<game_id>": ("GET", AuthMiddleware(get_status)),
    "/intensity": ("GET", AuthMiddleware(get_intensity)),
    "/catch": ("POST", AuthMiddleware(catch)),
    "/player": ("GET", AuthMiddleware(get_player)),
    "/end": ("GET", AuthMiddleware(end_game)),
    "/summary": ("POST", AuthMiddleware(game_summary))
}
