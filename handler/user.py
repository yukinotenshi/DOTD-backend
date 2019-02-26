from middleware.auth import AuthMiddleware
from misc import generate_random_string
from redis_wrapper import RedisClient
from peewee import PeeweeException
from core.util import *
from model import User


redis_client = RedisClient()


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
        redis_client.set(access_token, user.username)
    except PeeweeException as e:
        return respond_error(str(e), 500)

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
        return respond_error("User not found", 404)

    access_token = generate_random_string()
    redis_client.set(access_token, user.username)

    data = user.to_dict()
    data["access_token"] = access_token
    return respond_data(data)


def profile():
    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_error("Session not found", 400)

    username = redis_client.get(access_token)
    user = User.get_or_none(User.username == username)

    return respond_data(user.to_dict())


routes = {
    "/login": ("POST", login),
    "/register": ("POST", register),
    "/profile": ("GET", AuthMiddleware(profile)),
}
