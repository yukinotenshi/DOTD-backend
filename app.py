import dotenv

dotenv.load_dotenv()

from handler import user_routes, room_routes, game_routes
from core.router import Router
from flask_cors import CORS
from flask import Flask
import os


def initialize_app():
    _app = Flask(__name__)
    router = Router(_app)
    router.get("/", lambda: "DOTD Backend Service Runnning")
    router.group("/user", user_routes)
    router.group("/room", room_routes)
    router.group("/game", game_routes)
    CORS(_app)
    router.execute()
    return _app


app = initialize_app()


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT")), host=os.getenv("HOST"))
