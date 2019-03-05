import dotenv

dotenv.load_dotenv()

from handler import user_routes, room_routes
from core.router import Router
from flask_cors import CORS
from flask import Flask
import os


app = Flask(__name__)
CORS(app)
router = Router(app)


router.get("/", lambda: "DOTD Backend Service Runnning")
router.group("/user", user_routes)
router.group("/room", room_routes)


if __name__ == "__main__":
    router.execute()
    app.run(port=int(os.getenv("PORT")), host=os.getenv("HOST"))
