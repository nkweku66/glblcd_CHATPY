from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import paho.mqtt.client as mqtt
import json
from flask_socketio import SocketIO, send


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!123"
socketio = SocketIO(app, cors_allowed_origin="*", async_mode="threading")

# MQTT client setup
mqtt_client = mqtt.Client()

# Define MQTT connection parameters
MQTT_BROKER_HOST = "mqtt.eclipseprojects.io"

MQTT_BROKER_PORT = 1883
MQTT_CHAT_TOPIC = "glblcd"


# Function to set up MQTT
def setup_mqtt():
    global mqtt_client
    if not mqtt_client.is_connected():
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

        mqtt_client.loop_start()


# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_CHAT_TOPIC)
    # Subscribe to the chat topic upon successful connection


def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    message = msg.payload.decode()


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


# Define a global variable for MQTT_CHAT_TOPIC
@app.route("/search", methods=["POST"])
def search():
    global query
    query = request.form.get("query")
    print("Query: ", query)
    with open("./static/json/groups.json") as json_file:
        groups = json.load(json_file)
        results = [
            group["groupName"]
            for group in groups
            if query == group["groupName"].lower()
        ]
    if results:
        result = results[0]
        print("Finally", result)
        setup_mqtt()

    else:
        print("No result")
    global user
    return render_template("chat.html", results=results, user=user)


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
        global user
        user = username
        return render_template("chat.html", user=user)
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
        # setup_mqtt()
        mqtt_client.publish(MQTT_CHAT_TOPIC, message)
        print(message)
    return "", 204


# diconnect a client
@app.route("/disconnect")
def disconnect():
    mqtt_client.disconnect()
    print("disconnect")

    return redirect("/")


@socketio.on("message")
def handle_message(message):
    if message != "User connected!":
        send(message, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
