from flask import Flask, render_template, request
import yaml
from ruamel.yaml import YAML


app = Flask(__name__)

def update_version(version):
    try:
        file_path = '../domain.yml'
        with open(file_path, 'r') as f:
            domain_data = yaml.safe_load(f)

        domain_data['version'] = version

        with open(file_path, 'w') as f:
            f.write(f"version: '{version}'\n")  # Writing version as the first line
            yaml.dump(domain_data, f)

        return f"Version updated to '{version}' successfully!"
    except Exception as e:
        return f"Error updating version: {str(e)}"

def move_version_to_top():
    try:
        file_path = '../domain.yml'
        with open(file_path, 'r') as f:
            lines = f.readlines()

        version_line = next((line for line in lines if line.strip().startswith('version:')), None)

        if version_line:
            lines.remove(version_line)
            lines.insert(0, version_line)

            with open(file_path, 'w') as f:
                f.writelines(lines)

            return "Version moved to the top successfully!"
        else:
            return "Version not found in the file!"
    except Exception as e:
        return f"Error moving version to top: {str(e)}"



def remove_response(response_name):
    try:
        file_path = '../domain.yml'
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(file_path, 'r') as f:
            domain_data = yaml.load(f)

        if response_name in domain_data['responses']:
            del domain_data['responses'][response_name]
            with open(file_path, 'w') as f:
                yaml.dump(domain_data, f)
           # move_version_to_top()  # Move version to top after modification
            return f"Response '{response_name}' removed successfully!"
        else:
            return f"Response '{response_name}' not found!"
    except Exception as e:
        return f"Error removing response: {str(e)}"


def remove_intent(intent_name):
    try:
        file_path = '../domain.yml'
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(file_path, 'r') as f:
            domain_data = yaml.load(f)

        for intent in domain_data['intents']:
            if intent == intent_name:
                domain_data['intents'].remove(intent_name)
                with open(file_path, 'w') as f:
                    yaml.dump(domain_data, f)
                move_version_to_top()  # Move version to top after modification
                return f"Intent '{intent_name}' removed successfully!"

        return f"Intent '{intent_name}' not found!"
    except Exception as e:
        return f"Error removing intent: {str(e)}"

@app.route('/')
def index():
    return render_template('las.html')

@app.route('/remove_response', methods=['POST'])
def remove_response_route():
    response_name = request.form.get('response_name')
    if response_name:
        message = remove_response(response_name)
    else:
        message = "Please provide a response name."
    return render_template('las.html', message=message)

@app.route('/remove_intent', methods=['POST'])
def remove_intent_route():
    intent_name = request.form.get('intent_name')
    if intent_name:
        message = remove_intent(intent_name)
    else:
        message = "Please provide an intent name."
    return render_template('las.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
