from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

#Creating topics from user registrations



#Routing to signIn screen
@app.route('/')
def login():
     return render_template('login.html')

#Routing to signUp screen
@app.route('/signup')
def signup():
     return render_template('signup.html')

#Function to validate user logins
@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    with open("./static/json/data.json") as json_file:
        users = json.load(json_file)
        print(users)
    
    authenticated_user = next((user for user in users if user["username"] == username and user["password"] == password), None)

    if authenticated_user:
        return render_template("chat.html")
    else:
        return "error"


# Function to get and add Sign up details to database
@app.route('/register', methods=['POST', 'GET'])
def register():
     username = request.form.get('username')
     password = request.form.get('password')
     confirmPassword = request.form.get('confirmPassword')
     
     newUser = dict()

     if (password == confirmPassword and len(password) > 0 and len(confirmPassword) > 0):
          with open("./static/json/data.json", 'r') as json_file:
                users = json.load(json_file)
                newUser["username"] = username
                newUser["password"] = password

                users.append(newUser)

              
                
          with open("./static/json/data.json", 'w') as json_file:
                    json.dump(users, json_file, indent=4)
          return redirect('/')
     else:
           return "error"





if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
