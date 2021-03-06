from middleware.auth import AuthMiddleware
from core.util import *
from misc import generate_random_string
from redis_model import Room, Player, Game, ActiveSkill
from skeleton.character import *
from random import random


def cast_skill():
    session = load_session()
    player = Player(session.username)
    player.load()
    game = Game(player.room_id)
    game.load()

    char_class = characters_class[player.character]
    chara = char_class(player)
    skill_value = chara.calc_skill_value()

    game.active_skill = ActiveSkill(generate_random_string(8))
    game.active_skill.name = chara.skill
    game.active_skill.value = skill_value
    game.active_skill.caster = session.username
    data = game.to_dict()
    if player.team_id[-7:] == "chasing":
        game.active_skill.target = data['room']['hiding_team']
        game.active_skill.target = [x for x in game.active_skill.target if x['alive']]
        i = 0
        found = False
        for i, p in enumerate(game.active_skill.target):
            if p['character'] == 'Trickster':
                player = Player(p['username'])
                player.load()
                char_class = characters_class[player.character]
                chara = char_class(player)
                skill_value = chara.calc_skill_value()
                if skill_value >= random():
                    found = True
                    break
        if found:
            del game.active_skill.target[i]
    else:
        game.active_skill.target = data['room']['chasing_team']

    game.save()
    game.active_skill.save()
    return jsonify(game.to_dict())


routes = {"/cast": ("POST", AuthMiddleware(cast_skill))}
