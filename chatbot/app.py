from flask import Flask, render_template, request, jsonify
import requests, json

app = Flask(__name__, static_folder='static')


def load_config():
    with open('config.json') as f:
        config = json.load(f)
    return config


config = load_config()
RASA_API_URL = config['rasa_api']
print(config['las'])


@app.route('/')
def index():
    return render_template(config['page'])


@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.json['message']
    print("User Message:", user_message)
    print(config['las'])

    #send user message to rasa and get bot response
    rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
    rasa_response_json = rasa_response.json()

    print("RASA RESPONSE:", rasa_response_json)

    bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'sorry , bro I didn \'t understand that .'

    return jsonify({'response': bot_response})


if __name__ == "__name__":
    app.run(debug=True, port=config['port'])
