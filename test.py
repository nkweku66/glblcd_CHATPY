from flask import Flask, render_template, request, session, redirect, url_for, flash
import paho.mqtt.client as mqtt
import json
import uuid  # for generating unique user topics

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MQTT Broker settings
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_PREFIX = "chat/"

# MQTT client setup
mqtt_client = mqtt.Client()

# Callback when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Connection failed")

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Database setup (using a JSON file)
USER_DATABASE_FILE = "user_data.json"

def create_database():
    data = []
    with open(USER_DATABASE_FILE, "w") as json_file:
        json.dump(data, json_file)

create_database()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        if is_username_taken(username):
            flash('Username is already taken. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        # Generate a unique user topic (using UUID)
        user_topic = MQTT_TOPIC_PREFIX + str(uuid.uuid4())

        # Subscribe the user to the default chat topic
        mqtt_client.subscribe(user_topic)

        # Store user information in the database (using JSON)
        store_user_in_database(username, password, user_topic)

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Check if a username is already taken (using JSON)
def is_username_taken(username):
    with open(USER_DATABASE_FILE, "r") as json_file:
        data = json.load(json_file)
        for user in data:
            if user['username'] == username:
                return True
    return False

# Store user information in the database (using JSON)
def store_user_in_database(username, password, user_topic):
    with open(USER_DATABASE_FILE, "r") as json_file:
        data = json.load(json_file)
    new_user = {'username': username, 'password': password, 'user_topic': user_topic}
    data.append(new_user)
    with open(USER_DATABASE_FILE, "w") as json_file:
        json.dump(data, json_file)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are valid
        user = validate_user(username, password)

        if user:
            # Set the user as logged in using Flask session
            session['user'] = user
            flash('Login successful.', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Check if the username and password are valid (using JSON)
def validate_user(username, password):
    with open(USER_DATABASE_FILE, "r") as json_file:
        data = json.load(json_file)
        for user in data:
            if user['username'] == username and user['password'] == password:
                return user
    return None

@app.route('/get_user_topic', methods=['GET'])
def get_user_topic():
    username_to_search = request.args.get('username')

    # Load user data from the JSON database
    with open(USER_DATABASE_FILE, "r") as json_file:
        data = json.load(json_file)
        for user in data:
            if user['username'] == username_to_search:
                return jsonify({'userTopic': user['user_topic']})

    return jsonify({'userTopic': None})


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


