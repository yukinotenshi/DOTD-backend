from core.router import Router
from flask import Flask
import dotenv
import os


app = Flask(__name__)
dotenv.load_dotenv()
router = Router(app)


router.get("/", lambda: "DOTD Backend Service Runnning")


if __name__ == "__main__":
    router.execute()
    app.run(port=int(os.getenv("PORT")), host=os.getenv("HOST"))
