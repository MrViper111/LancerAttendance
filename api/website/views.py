import asyncio
import json
import os
import datetime
import random
from crypt import methods
from threading import Thread
from flask import Blueprint, render_template, request, jsonify
from functools import update_wrapper, wraps

from database import Database
from positions import Positions
from structures.users import Users

views = Blueprint("views", __name__)
db = Database.establish_connection(Database.URI, Database.NAME)
users = Users(db.users)

# Create a background event loop

@views.route("/")
def home():
    return render_template("home.html")


# the api stuff

@views.route("api/get_status", methods=["GET"])
def get_status():
    return jsonify({"status": 200})


@views.route("api/create_user", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": 400, "response": "Invalid JSON body"})

    name = data.get("name")
    email = data.get("email")
    position = data.get("position")

    created = users.create(name, email, position, False)
    if created:
        return jsonify({"status": 201, "response": "User created"})
    else:
        return jsonify({"status": 409, "response": "User with email already exists"})


@views.route("api/update_user", methods=["PUT"])
def update_user():
    data = request.get_json(silent=True)

    email = data.get("email")
    position = data.get("position")
    score = data.get("score")
    admin = data.get("admin")

    updated = users.update(email, position, score, admin)
    if updated:
        return jsonify({"status": 201, "response": "User updated"})
    else:
        return jsonify({"status": 409, "response": "Unable to update user"})


@views.route("api/delete_user", methods=["DELETE"])
def delete_user():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": 400, "response": "Invalid JSON body"})

    email = data.get("email")

    deleted = users.delete(email)
    if deleted:
        return jsonify({"status": 200, "response": "User deleted"})
    else:
        return jsonify({"status": 210, "response": "User does not exist"})


@views.route("api/get_users", methods=["GET"])
def get_users():
    return {"status": 200, "response": users.get_all()}