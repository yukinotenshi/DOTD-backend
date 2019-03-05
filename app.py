import dotenv

dotenv.load_dotenv()

from handler import user_routes, room_routes
from core.router import Router
from flask_cors import CORS
from flask import Flask
import os


def initialize_app():
    app = Flask(__name__)
    router = Router(app)
    router.get("/", lambda: "DOTD Backend Service Runnning")
    router.group("/user", user_routes)
    router.group("/room", room_routes)
    CORS(app)
    router.execute()
    return app

app = initialize_app()

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT")), host=os.getenv("HOST"))
