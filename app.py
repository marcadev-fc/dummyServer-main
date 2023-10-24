import os
import uuid
import logging
import json
from flask import Flask, request, jsonify, render_template
from threading import Timer
from ddtrace import patch_all


patch_all()


# ADDING COLOR TO LOGS
os.system('')
logging.addLevelName(logging.DEBUG, "\33[32m%s" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.INFO, "\33[36m%s" % logging.getLevelName(logging.INFO))
logging.addLevelName(logging.WARNING, "\33[33m%s" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\33[31m%s" % logging.getLevelName(logging.ERROR))


logging.basicConfig(
    format='%(levelname)-8s %(asctime)s,%(msecs)d [%(filename)s:%(lineno)d] %(message)s\033[0m',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=getattr(logging, "INFO"))


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "SECRET_KEY")  # Security key for Flask


users = dict()
username_set = set()


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


RepeatedTimer(60*15, lambda: logging.info("KEEP ALIVE"))


@app.get('/')
def main():
    return render_template('index.html')


@app.get('/reset')
def reset_server(user_id=None):
    global users
    global username_set
    users = dict()
    username_set = set()
    return jsonify({"success": True})


@app.post('/users')
def create_users():
    new_user = dict()
    new_user["name"] = request.get_json().get("name", "UNK")
    new_user["username"] = request.get_json().get("username", str(uuid.uuid4()))
    if new_user["username"] in username_set:
        logging.info(f"{new_user['username']} ALREADY EXISTS")
        response = jsonify({"success": False, "desc": "Duplicated user"})
        response.status_code = 409
        return response
    username_set.add(new_user["username"])
    new_user["id"] = str(uuid.uuid4())
    users[new_user["id"]] = (new_user)
    return jsonify({"success": True, "userId": new_user["id"]})


@app.get('/users/<user_id>')
@app.get('/users')
def get_users(user_id=None):
    if user_id:
        try:
            return jsonify({"success": True, "users": [users[user_id]]})
        except KeyError:
            logging.info(f"{user_id} NOT FOUND")
            response = jsonify({"success": False, "desc": "User not found"})
            response.status_code = 404
            return response
    return jsonify({"success": True, "users": [users[key] for key in users]})


def create_app():
    return app
