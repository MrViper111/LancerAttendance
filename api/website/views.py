import asyncio
import json
import os
from datetime import datetime
import random
from crypt import methods
from threading import Thread
from flask import Blueprint, render_template, request, jsonify, redirect
from functools import update_wrapper, wraps

from database import Database
from flask_cors import CORS
from positions import Positions
from structures.users import Users

views = Blueprint("views", __name__)
db = Database.establish_connection(Database.URI, Database.NAME)
users = Users(db.users)

CORS(views)

# Create a background event loop

@views.route("/")
def home():
    return render_template("home.html")

@views.route("login", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("login.html")

    if request.form["email"] == "jake" and request.form["password"] == "jin":
        return render_template("adminpanel.html")

    return render_template("login.html")

@views.route("admin/home")
def admin_home():
    return redirect("/login")

@views.route("admin/profile/<id>")
def admin_profile(id):
    return render_template("profile.html", id=id)

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
    id = data.get("id")
    position = data.get("position")

    created = users.create(name, id, position, False)
    if created:
        return jsonify({"status": 201, "response": "User created"})
    else:
        return jsonify({"status": 409, "response": "User with ID already exists"})


@views.route("api/update_user", methods=["PUT"])
def update_user():
    data = request.get_json(silent=True)

    id = data.get("id")
    position = data.get("position")
    score = data.get("score")
    admin = data.get("admin")

    updated = users.update(id, position, score, admin)
    if updated:
        return jsonify({"status": 201, "response": "User updated"})
    else:
        return jsonify({"status": 409, "response": "Unable to update user"})


@views.route("api/delete_user", methods=["DELETE"])
def delete_user():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": 400, "response": "Invalid JSON body"})

    id = data.get("id")

    deleted = users.delete(id)
    if deleted:
        return jsonify({"status": 200, "response": "User deleted"})
    else:
        return jsonify({"status": 210, "response": "User does not exist"})


@views.route("api/get_users", methods=["GET"])
def get_users():
    return {"status": 200, "response": users.get_all()}


@views.route("api/get_user")
def get_user():
    id = request.args.get("id")
    return {"status": 200, "response": users.get({"id": id})}


@views.route("api/check_in", methods=["POST"])
def check_in():
    data = request.get_json(silent=True)
    id = data.get("id")

    print("checking in ", id)

    checked_in = users.check_in(id)
    return {"status": 200, "response": "Checked in" if checked_in else "Checked out"}


@views.route("api/is_present")
def is_checked_in():
    id = request.args.get("id")
    user = users.get({"id": id})

    if not user:
        return False

    if not user.get("attendance"):
        return {"status": 200, "response": False}

    last_obj = user["attendance"][-1]
    if last_obj["date"] == datetime.now().strftime("%x") and not last_obj["out"]:
        return {"status": 200, "response": True}

    return {"status": 200, "response": False}