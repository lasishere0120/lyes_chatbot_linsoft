from flask import Flask, render_template
import yaml

app = Flask(__name__)

def get_intent_names():
    intents = []
    with open('nlu.yml', 'r') as f:
        data = yaml.safe_load(f)
        if 'nlu' in data and 'nlu' in data['nlu']:
            for item in data['nlu']['nlu']:
                if 'intent' in item:
                    intents.append(item['intent'])
    return intents

@app.route('/')
def index():
    intent_names = get_intent_names()
    return render_template('azer.html', intent_names=intent_names)

if __name__ == '__main__':
    app.run(debug=True)
