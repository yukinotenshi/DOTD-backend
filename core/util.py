from flask import request, jsonify


def respond_data(data, code=200):
    return jsonify({"status": code, "data": data}), code


def respond_error(message, code=500):
    return jsonify({"status": code, "message": message}), code


def check_json_in_request(fields):
    for field_name in fields:
        if not request.json.get(field_name):
            return False, respond_error("{} not found in JSON".format(field_name), 400)

    return True, None
