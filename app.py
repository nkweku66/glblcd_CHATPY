from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json


app = Flask(__name__)


# MQTT client setup
mqtt_client = mqtt.Client()

# Define MQTT connection parameters
MQTT_BROKER_HOST = "mqtt.eclipseprojects.io"
MQTT_BROKER_PORT = 1883
MQTT_CHAT_TOPIC = ""

# Function to set up MQTT
def setup_mqtt():
    global mqtt_client
    if not mqtt_client.is_connected():
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        mqtt_client.loop_start()


# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to the chat topic upon successful connection


def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")


# Set MQTT callback functions
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


# Routing to signIn screen
@app.route("/")
def login():
    return render_template("login.html")


# Routing to signUp screen
@app.route("/signup")
def signup():
    return render_template("signup.html")


"""
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")

    with open("./static/json/groups.json") as json_file:
        groups = json.load(json_file)
        results = [
            group["groupName"]
            for group in groups
            if query == group["groupName"].lower()
        ]
    try:
        global MQTT_CHAT_TOPIC
        MQTT_CHAT_TOPIC = results[0]
    except IndexError:
        return render_template("chat.html")
    print(results)

    return render_template("chat.html", results=results)

    """


# Define a global variable for MQTT_CHAT_TOPIC
@app.route("/search", methods=["POST", "GET"])
def search():
    query = request.form.get("query")

    with open("./static/json/groups.json") as json_file:
        groups = json.load(json_file)
        results = [
            group["groupName"]
            for group in groups
            if query == group["groupName"].lower()
        ]

    
    try:
        MQTT_CHAT_TOPIC = results[0]
        print(MQTT_CHAT_TOPIC)
        setup_mqtt()
        mqtt_client.subscribe(MQTT_CHAT_TOPIC)

    except IndexError:
        MQTT_CHAT_TOPIC = ""  # Set to an empty string if no results are found

    # Create a response dictionary to send JSON data

    response_data = {
        "results": results,
    }

    return jsonify(response_data)


# Function to validate user logins
@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form.get("username")
    password = request.form.get("password")

    with open("./static/json/data.json") as json_file:
        users = json.load(json_file)

    authenticated_user = next(
        (
            user
            for user in users
            if user["username"] == username and user["password"] == password
        ),
        None,
    )

    if authenticated_user:
        return render_template("chat.html", username=username)
    else:
        return "error"


# Function to get and add Sign up details to database
@app.route("/register", methods=["POST", "GET"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")

    newUser = dict()

    if password == confirmPassword and len(password) > 0 and len(confirmPassword) > 0:
        with open("./static/json/data.json", "r") as json_file:
            users = json.load(json_file)
            newUser["username"] = username
            newUser["password"] = password

            users.append(newUser)

        with open("./static/json/data.json", "w") as json_file:
            json.dump(users, json_file, indent=4)
        return redirect("/")
    else:
        return "error"


@app.route("/update_content", methods=["POST"])
def update_content():
    message = request.form.get("message")
    if message:
        
        mqtt_client.publish(MQTT_CHAT_TOPIC, message)
        print(message)
    response_data = {"new_content": message}
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
