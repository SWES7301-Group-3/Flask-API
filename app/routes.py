from flask import Blueprint, jsonify, request

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Flask REST API Boilerplate for Group 3 of SWES731!"})

@main.route("/echo", methods=["POST"])
def echo():
    data = request.get_json()
    return jsonify({"you_sent": data}), 201
