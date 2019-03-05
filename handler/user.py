from middleware.auth import AuthMiddleware
from misc import generate_random_string
from redis_model import Session
from peewee import PeeweeException
from core.util import *
from model import User


def register():
    included, error = check_json_in_request(["username", "password"])
    if not included:
        return error

    username = request.json.get("username")
    password = request.json.get("password")

    try:
        user = User(username=username, password=password)
        user.save()
        access_token = generate_random_string()
        session = Session(access_token, {"username": username})
        session.save()
    except PeeweeException as e:
        return respond_message(str(e), 500)

    data = user.to_dict()
    data["access_token"] = access_token
    return respond_data(data)


def login():
    included, error = check_json_in_request(["username", "password"])
    if not included:
        return error

    username = request.json.get("username")
    password = request.json.get("password")

    user = User.get_or_none(User.password == password, User.username == username)
    if not user:
        return respond_message("User not found", 404)

    access_token = generate_random_string()
    session = Session(access_token, {"username": username})
    session.save()

    data = user.to_dict()
    data["access_token"] = access_token
    return respond_data(data)


def profile():
    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_message("Session not found", 400)

    session = Session(access_token)
    session.load()
    username = session.username
    user = User.get_or_none(User.username == username)

    return respond_data(user.to_dict())


routes = {
    "/login": ("POST", login),
    "/register": ("POST", register),
    "/profile": ("GET", AuthMiddleware(profile)),
}
