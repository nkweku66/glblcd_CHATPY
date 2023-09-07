from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Initialize an empty list to store chat messages
messages = []


@app.route('/')
def index():
    return render_template('login-test.html', messages=messages)


@app.route('/send', methods=['POST'])
def send():
    user_message = request.form.get('message')
    if user_message:
        messages.append(user_message)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
