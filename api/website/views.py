import json
import os
import datetime
import random
from crypt import methods

from flask import Blueprint, render_template, request, jsonify
from functools import update_wrapper, wraps

from database import Database
from positions import Positions
from structures.users import Users

views = Blueprint("views", __name__)
db = Database.establish_connection(Database.URI, Database.NAME)
users = Users(db["users"])

@views.route("/")
def home():
    return render_template("home.html")

# the api stuff

@views.route("api/get_status", methods=["GET"])
def get_status():
    data = {'name': 'Alice', 'age': 25}
    return jsonify(data)

@views.route("api/create_user", methods=["POST"])
async def create_user():
    name = request.args.get("name")
    email = request.args.get("email")
    position = request.args.get("position")

    await users.create(name, email, position, False)

@views.route("api/get_users")
def get_users():
    return jsonify({"status": 200, "response": users.get_all()})
