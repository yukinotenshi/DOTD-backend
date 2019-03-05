from random import choice
from middleware.auth import AuthMiddleware
from misc import generate_random_string
from core.util import *
from redis_model import Room, Player, Game


def start_game():
    included, error = check_json_in_request(["room_id"])
    if not included:
        return error

    session = load_session()

    room = Room(request.json["room_id"])
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
    lat = request.json.get('lat')
    lng = request.json.get('lng')

    session = load_session()

    p = Player(session.username)
    p.load()
    p.lat = lat
    p.lng = lng
    p.save()

    return respond_data(p.to_dict())





routes = {
    '/location': ('POST', AuthMiddleware(submit_location)),
    '/start': ('POST', AuthMiddleware(start_game))
}
