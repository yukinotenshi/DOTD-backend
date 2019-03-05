from flask import request, jsonify
from redis_model import Session


def respond_data(data, code=200):
    return jsonify({"status": code, "data": data}), code


def respond_message(message, code=500):
    return jsonify({"status": code, "message": message}), code


def check_json_in_request(fields):
    for field_name in fields:
        if not request.json.get(field_name):
            return False, respond_message("{} not found in JSON".format(field_name), 400)

    return True, None


def load_session():
    access_token = request.headers.get("Authorization")
    if not access_token:
        return respond_message("Session not found", 400)

    session = Session(access_token)
    session.load()
    return session
