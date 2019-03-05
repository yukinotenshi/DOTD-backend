import json
import load_env
from redis_wrapper import RedisClient


class RedisBaseModel:
    def __init__(self, key, data=None):
        self._key = key
        self._r = RedisClient()
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
