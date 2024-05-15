from flask import Flask, render_template
import yaml

app = Flask(__name__)

def get_response_names(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        response_names = [response.replace('utter_', '') for response in data.get('responses', {}).keys()]
    return response_names

@app.route('/')
def index():
    file_path = '../domain.yml'
    response_names = get_response_names(file_path)
    return render_template('azer.html', response_names=response_names)

if __name__ == '__main__':
    app.run(debug=True)
