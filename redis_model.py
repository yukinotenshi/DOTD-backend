import simplejson as json
import load_env
from redis_wrapper import RedisClient


class RedisBaseModel:
    def __init__(self, key, data=None):
        self._key = key
        self._r = RedisClient.load()
        self._fields = []

    def _set_data(self, data):
        for key, val in data.items():
            if key in self._fields:
                setattr(self, key, val)
            else:
                raise Exception("Incomplete fields")

    def save(self):
        serializable = self.to_dict()
        serialized = json.dumps(serializable)
        return self._r.set(self._key + type(self).__name__, serialized)

    def load(self):
        data = self._r.get(self._key + type(self).__name__)
        data = json.loads(data)
        self._set_data(data)

    def delete(self):
        self._r.delete(self._key)

    def to_dict(self):
        data = {}
        for field_name in self._fields:
            data[field_name] = getattr(self, field_name)

        return data


class Session(RedisBaseModel):
    def __init__(self, key, data=None):
        self.username = ""
        super().__init__(key, data)
        self._fields = ["username"]
        if data:
            self._set_data(data)


class Player(RedisBaseModel):
    def __init__(self, key, data=None):
        self.username = ""
        self.room_id = ""
        self.team_id = ""
        self.lat = 0.0
        self.lng = 0.0
        self.alive = True
        super().__init__(key, data)
        self._fields = ["username", "room_id", "team_id", "lat", "lng"]
        if data:
            self._set_data(data)


class Room(RedisBaseModel):
    def __init__(self, room_id, data=None):
        self.room_id = ""
        self.chasing_team = []
        self.hiding_team = []
        self.owner = ""
        super().__init__(room_id, data)
        self._fields = ["room_id", "chasing_team", "hiding_team", "owner"]
        if data:
            self._set_data(data)


class Game(RedisBaseModel):
    def __init__(self, game_id, data=None):
        self.game_id = game_id
        self.room = None
        self.players = []
        super().__init__(game_id, data)
        self._fields = ["game_id", "room", "players"]
        if data:
            self._set_data(data)

    def load_players(self):
        player_usernames = self.room.chasing_team + self.room.hiding_team
        self.players = []
        for username in player_usernames:
            p = Player(username)
            p.load()
            self.players.append(p)

    def load(self):
        data = self._r.get(self._key + type(self).__name__)
        data = json.loads(data)
        room = Room(data["room"]["room_id"])
        room.load()
        self.room = room
        self.players = []
        for p in data['players']:
            player = Player(p['username'])
            player.load()
            self.players.append(player)

    def to_dict(self):
        data = {}
        for field_name in self._fields:
            if field_name == "room":
                data[field_name] = self.room.to_dict()
            elif field_name == "players":
                data[field_name] = [p.to_dict() for p in self.players]
            else:
                data[field_name] = getattr(self, field_name)

        return data
