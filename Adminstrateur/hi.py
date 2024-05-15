import base64
import json

from cryptography.fernet import Fernet
from flask import Flask, render_template, request, jsonify
import yaml
from ruamel.yaml import YAML
import imaplib
import email
from datetime import datetime, timedelta, timezone
app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return render_template('signin.html')


# pour l ajouter de dataset
def intent_exists(intent_name, nlu_data):
    # Check if intent exists in the NLU data
    for index, line in enumerate(nlu_data):
        if line.strip() == f"- intent: {intent_name}":
            return index
    return -1


def add_intent(IN, EX):
    with open('../data/nlu.yml', 'r') as f:
        nlu_data = f.readlines()
    exist=intent_exists(IN,nlu_data)
    print(exist)
    # Check if intent already exists
    if exist!=-1:
        return f"The intent '{IN}' already exists."
    else:

        formatted_examples = ["    - " + example.strip() for example in EX.split('\n')]

        with open('../data/nlu.yml', 'a') as f:
            f.write(f"\n- intent: {IN}\n")
            f.write("  examples: |\n")
            f.write('\n'.join(formatted_examples) + '\n')
        return "Intent added successfully!"
    '''
def add_intent(intent_name, examples):
    try:
        file_path = 'nlu.yml'
        yaml = YAML()
        with open(file_path, 'r') as f:
            nlu_data = yaml.load(f)
            formatted_examples = "\n    - ".join(examples.split('\n'))
            intent_entry = {
                'intent': intent_name,
                'examples': f"| \n    - {formatted_examples}\n"
            }
            nlu_data['nlu'].append(intent_entry)
            with open(file_path, 'w') as f:
                f.write(yaml.dump(nlu_data))
            return f"Intent '{intent_name}' added successfully!"
    except Exception as e:
        return f"Error adding intent: {str(e)}"
'''






def add_story(SN, I, A):
    with open('../data/stories.yml', 'r') as f:
        existing_stories = f.read()

    # Construct the story string
    new_story = f"\n\n- story: {SN}\n"
    new_story += "  steps:\n"
    new_story += f"  - intent: {I}\n"
    new_story += f"  - action: {A}\n"

    # Check if the story already exists, if not, add it
    if new_story in existing_stories:
        return "Story already exists!"

    # Add the new story
    with open('../data/stories.yml', 'a') as f:
        f.write(new_story)

    return "Story added successfully!"


'''
def add_response(IN, RN, RC):
    file_path = 'domain.yml'
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(file_path, 'r') as f:
        domain_data = yaml.load(f)


    with open(file_path, 'r') as f:
        lines = yaml.load(f)

    # Extract the version
    version_line = lines[0].strip()

    # Find the index of the 'intents' line
    intents_index = lines.index('intents:\n')

    # Extract existing intents and responses
    existing_data = yaml.safe_load(''.join(lines[intents_index:]))
    intents = existing_data.get('intents', [])
    responses = existing_data.get('responses', {})
    print(responses)

    # Check if the intent already exists, if not, add it
    if IN not in intents:
        intents.append(IN)

    # Construct response key
    response_key = f"utter_{RN}"

    # Check if the response already exists, if not, add it
    if response_key in responses:
        return "Response name already exists!"

    responses[response_key] = []

    # Split the RC by newline and add each line as a separate response
    for line in RC.split('\n'):
        line = line.strip()  # Remove leading and trailing whitespace
        if line:  # Skip empty lines
            responses[response_key].append({'text': line})

    new_data = {'intents': intents, 'responses': responses}

    # Find the index of the 'session_config' line
    session_config_index = lines.index('session_config:\n')

    with open('domain.yml', 'w') as f:
        f.write(version_line + '\n\n')  # Add an extra newline after the version line
        f.write('intents:\n')
        for intent in intents:
            f.write(f'  - {intent}\n')  # Ensure proper indentation

        f.write('\nresponses:\n')
        for response_key, response_list in responses.items():
            f.write(f'  {response_key}:\n')
            for response in response_list:
                f.write(f'  - text: "{response["text"]}"\n')  # Ensure proper indentation for response text
                # You can add other fields such as image here if needed

        # Write the session_config block
    #f.writelines(lines[session_config_index:])  # Write the session_config block as it is

    return "Intent and response added successfully!"
'''
def add_response(response_name, response_text, intent_name):
    try:
        file_path = '../chatbot/domain.yml'
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(file_path, 'r') as f:
            domain_data = yaml.load(f)
            response_key = f"utter_{response_name}"
            if response_key not in domain_data['responses']:
                domain_data['responses'][response_key] = [{'text': response_text}]
                if intent_name not in domain_data['intents']:
                    domain_data['intents'].append(intent_name)
                with open(file_path, 'w') as f:
                    yaml.dump(domain_data, f)
                return f"Response '{response_name}' added successfully!"
            else:
                return f"Response '{response_name}' already exists!"
    except Exception as e:
        return f"Error adding response: {str(e)}"


@app.route('/add_data', methods=['POST'])
def handle_add_data():
    # Get the form data
    intent_name = request.form['name_intent']
    examples = request.form['examples']
    response_name = request.form['response_name']
    response_text = request.form['response_text']

    # Check if any field is empty
    if not all([intent_name, examples, response_name, response_text]):
        message = "Please provide values for all fields."
        return render_template('Ajouter_final.html', message=message)

    # Add intent
    add_intent_result = add_intent(intent_name, examples)

    # Add response
    add_response_result = add_response(response_name, response_text, intent_name)

    # Add story
    story_name = "admin story"
    action_global = "utter_" + response_name
    intent_global = intent_name
    add_story(story_name, intent_global, action_global)
# Execute the jarb.sh script in a new terminal
    try:
            subprocess.Popen(["x-terminal-emulator", "-e", "/bin/bash", "/home/lasishere/Desktop/jarb.sh"])
            message2 = "jarb.sh started in a new terminal."
    except Exception as e:
            message2 = f"Error starting jarb.sh: {e}"
    # Concatenate all the results into a single response
    response = f"{add_intent_result} {add_response_result}"

    return render_template('Ajouter_final.html',message1=message2, message=response)


# modfier dataset


def update_intent(IN, EX):
    # Load NLU data
    with open('../data/nlu.yml', 'r') as f:
        nlu_data = f.readlines()

    # Check if intent already exists
    intent_index = intent_exists(IN, nlu_data)
    if intent_index != -1:
        # Intent already exists, update its examples
        formatted_examples = ["    - " + example.strip() + "\n" for example in EX.split('\n')]

        # Find the start index of the examples section
        start_index = nlu_data.index(f"- intent: {IN}\n") + 2
        # Find the end index of the examples section
        end_index = len(nlu_data)  # Default to end of file
        for i in range(start_index + 1, len(nlu_data)):
            if nlu_data[i].startswith("- intent:"):
                end_index = i
                break
        # Replace existing examples with new examples
        nlu_data[start_index:end_index] = formatted_examples
        # Write updated NLU data back to the file
        with open('../data/nlu.yml', 'w') as f:
            f.writelines(nlu_data)
        return "Intent examples updated successfully!"
    else:
        return "Intent not exist"


def intent_exists(intent_name, nlu_data):
    # Check if intent exists in the NLU data
    for index, line in enumerate(nlu_data):
        if line.strip() == f"- intent: {intent_name}":
            return index
    return -1


def update_response_text(RN, RC):
    with open('../chatbot/domain.yml', 'r') as f:
        lines = f.readlines()

    # Find the index of the 'responses' section
    responses_index = lines.index('responses:\n')

    # Extract existing responses
    existing_responses = {}
    for i in range(responses_index + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith('utter_'):
            response_key = line.split(':')[0].strip()
            existing_responses[response_key] = []
        elif line.startswith('- text:'):
            existing_responses[response_key].append(line.strip()[8:])  # Extract response text
    response_key = f"utter_{RN}"

    # Check if the response exists
    if response_key not in existing_responses:
        return "Response does not exist!"

    # Find the index of the response to be updated
    response_index = lines.index(f'  {response_key}:\n')

    # Replace the existing response text with new text
    lines[response_index + 1] = f'  - text: "{RC.strip()}"\n'

    # Write the updated responses back to the domain.yml file
    with open('../chatbot/domain.yml', 'w') as f:
        f.writelines(lines)

    return "Response text updated successfully!"


@app.route('/update_data', methods=['POST'])
def handle_data():
    # Get the form data
    intent_name = request.form['intent_name']
    examples = request.form['new_examples']
    rep_name = request.form['resp_name']
    rep_text = request.form['resp_text']

    # Check if any field is empty
    if not all([intent_name, examples, rep_name, rep_text]):
        message = "Please provide values for all fields."
        return render_template('Modifier_final.html', message=message)

    # Update intent
    update_intent_result = update_intent(intent_name, examples)

    # Update response text
    add_rep_result = update_response_text(rep_name, rep_text)
# Execute the jarb.sh script in a new terminal
    try:
            subprocess.Popen(["x-terminal-emulator", "-e", "/bin/bash", "/home/lasishere/Desktop/jarb.sh"])
            message2 = "jarb.sh started in a new terminal."
    except Exception as e:
            message2 = f"Error starting jarb.sh: {e}"
    # Concatenate all the results into a single response
    response = f"{update_intent_result}, {add_rep_result}"

    return render_template('Modifier_final.html',message1=message2, message=response)


# supprimer dataset

def remove_intent(intent_name):
    try:
        with open('../data/nlu.yml', 'r') as f:
            nlu_data = f.readlines()

        # Find the index of the intent to be removed
        intent_index = -1
        for i, line in enumerate(nlu_data):
            if line.strip() == f"- intent: {intent_name}":
                intent_index = i
                break

        if intent_index != -1:
            # Find the start and end index of the intent block
            start_index = intent_index
            while start_index >= 0 and nlu_data[start_index].strip() != '':
                start_index -= 1
            end_index = intent_index
            while end_index < len(nlu_data) and nlu_data[end_index].strip() != '':
                end_index += 1

            # Remove the intent block from the list of lines
            del nlu_data[start_index + 1:end_index]

            # Write the updated data back to the file
            with open('../data/nlu.yml', 'w') as f:
                f.writelines(nlu_data)

            return f"Intent '{intent_name}' removed successfully!"
        else:
            return f"Intent '{intent_name}' not found!"
    except Exception as e:
        return f"Error removing intent: {str(e)}"





intent_name_global = None

@app.route('/remove_intent', methods=['POST'])
def remove_intent_route():
    global intent_name_global

    intent_name = request.form.get('intent_name')

    if intent_name:
        intent_name_global = intent_name  # Set the global variable value
        message = remove_intent(intent_name)

        # Execute the jarb.sh script in a new terminal
        try:
            subprocess.Popen(["x-terminal-emulator", "-e", "/bin/bash", "/home/lasishere/Desktop/jarb.sh"])
            message2 = "jarb.sh started in a new terminal."
        except Exception as e:
            message2 = f"Error starting jarb.sh: {e}"

    else:
        message = "Please provide an intent name."
        message2="didn't go "
    return render_template('Supprimer.html', message=message,message1=message2)



# remove response and intent from Domain.YML

def remove_response(response_nam):
    try:

        file_path = '../chatbot/domain.yml'
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(file_path, 'r') as f:
            domain_data = yaml.load(f)
            response_name=f"utter_"+response_nam
            print(response_name)

        if response_name in domain_data['responses']:
            del domain_data['responses'][response_name]
            with open(file_path, 'w') as f:
                yaml.dump(domain_data, f)
            # move_version_to_top()  # Move version to top after modification
            response_name_cleaned = response_name.replace("utter_", "")
            return f"Response '{response_name_cleaned}' removed successfully!"
        else:
            response_name_cleaned = response_name.replace("utter_", "")
            return f"Response '{response_name_cleaned}' not found!"
    except Exception as e:
        return f"Error removing response: {str(e)}"


def remove_intent_2(intent_name):
    try:
        file_path = '../chatbot/domain.yml'
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(file_path, 'r') as f:
            domain_data = yaml.load(f)

        for intent in domain_data['intents']:
            if intent == intent_name:
                domain_data['intents'].remove(intent_name)
                with open(file_path, 'w') as f:
                    yaml.dump(domain_data, f)

                return f"Intent '{intent_name}' removed successfully!"

        return f"Intent '{intent_name}' not found!"
    except Exception as e:
        return f"Error removing intent: {str(e)}"

import subprocess

@app.route('/remove_response', methods=['POST'])
def remove_response_route():
    response_name = request.form.get('response_name')
    if response_name:
        message1 = remove_response(response_name)
        intent_name = intent_name_global

        remove_intent_2(intent_name)

        # Execute the jarb.sh script in a new terminal
        try:
            subprocess.Popen(["x-terminal-emulator", "-e", "/bin/bash", "/home/lasishere/Desktop/jarb.sh"])
            message2 = "jarb.sh started in a new terminal."
        except Exception as e:
            message2 = f"Error starting jarb.sh: {e}"
    else:
        message1 = "Please provide a response name."
        message2 = ""  # No message for jarb.sh execution

    return render_template('Supprimer.html', message=message1, message1=message2)





#affiche intent name in comobox
def get_intent_names(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        intent_names = [entry['intent'] for entry in data['nlu']]
    return intent_names

def get_response_names(file_path):
    with open('../chatbot/domain.yml', 'r') as file:
        data = yaml.safe_load(file)
        response_names = [response.replace('utter_', '') for response in data.get('responses', {}).keys()]
    return response_names




@app.route('/get_response_names')
def get_response_names_route():
    file_path = '../chatbot/domain.yml'
    response_names = get_response_names(file_path)
    return {'response_names':response_names}

@app.route('/get_intent_names')
def get_intent_names_route():
    file_path = '../data/nlu.yml'
    intent_names = get_intent_names(file_path)
    return {'intent_names': intent_names}




@app.route('/acueil_login')
def acueil_log():

    return render_template('page de acueil.html')

@app.route('/ajouter')
def ajouter_final():
    emails = fetch_emails_with_subject()
    return render_template('Ajouter_final.html', emails=emails)


@app.route('/acueil')
def acueil():
    emails = fetch_emails_with_subject()
    return render_template('page de acueil.html', emails=emails)
@app.route('/nlu')
def nlu():
    # Read the content of the nlu.yml file
    with open('../data/nlu.yml', 'r') as file:
        nlu_content = file.read()

    emails = fetch_emails_with_subject()
    return render_template('NLU.html',nlu_content=nlu_content, emails=emails)
@app.route('/sotries')
def sotries():
    # Read the content of the nlu.yml file
    with open('../data/stories.yml', 'r') as file:
        nlu_content = file.read()

    emails = fetch_emails_with_subject()
    return render_template('sotries.html',nlu_content=nlu_content, emails=emails)
@app.route('/domain')
def domain():

    # Read the content of the nlu.yml file
    with open('../chatbot/domain.yml', 'r') as file:
        nlu_content = file.read()
    emails = fetch_emails_with_subject()
    return render_template('DOMAIN.html',nlu_content=nlu_content, emails=emails)


@app.route('/modifier')
def modifier():
    emails = fetch_emails_with_subject()
    return render_template('Modifier_final.html', emails=emails)


@app.route('/supprimer')
def supp():
    emails = fetch_emails_with_subject()
    return render_template('Supprimer.html', emails=emails)


@app.route('/Login')
def log():
    return render_template('signin.html')






@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Generate a random key
    key = b'las'
    padded_key = base64.urlsafe_b64encode(key.ljust(32, b'\0'))
    # Create a Fernet symmetric encryption object with the key
    cipher_suite = Fernet(padded_key)

    # Load users from JSON file
    with open('user.json', 'r') as f:
        users_data = json.load(f)
    username = request.json.get('username')
    password = request.json.get('password')

    # Find user by username
    user = next((u for u in users_data['users'] if u['username'] == username), None)

    if user:
        # Decrypt the stored password
        stored_password = cipher_suite.decrypt(user['password'].encode()).decode()

        if password == stored_password:
            return jsonify({'valid': True})

    return jsonify({'valid': False})

#create notivcation

# Gmail IMAP settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = 'machilyes000@gmail.com'
PASSWORD = 'tiyz bcej kmra rjxt'  # Replace with your app-specific password
SEARCH_SUBJECT = 'Reporter Chatbot'


# Function to fetch emails with a specific subject
def fetch_emails_with_subject():
    try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)

        # Select the inbox folder
        mail.select('inbox')

        # Search for emails with the specified subject
        status, data = mail.search(None, 'SUBJECT', f'"{SEARCH_SUBJECT}"')

        emails = []
        if status == 'OK':
            for num in data[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extract sender's name, subject, and time
                    sender = email.utils.parseaddr(msg['From'])[0]  # Extract only sender's name
                    subject = msg['Subject']
                    time = msg['Date']  # Time of email
                    formatted_time = format_time(time)

                    emails.append({"sender": sender, "subject": subject, "time": formatted_time})

        # Logout and close the connection
        mail.logout()

        return emails
    except Exception as e:
        print("Error fetching emails with subject:", e)
        return []


# Function to format time difference
def format_time(time_str):
    email_time = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S %z')
    current_time = datetime.now(timezone.utc)  # Make current_time aware
    time_difference = current_time - email_time

    if time_difference < timedelta(minutes=1):
        return "Just now"
    elif time_difference < timedelta(hours=1):
        minutes = int(time_difference.total_seconds() / 60)
        return f"{minutes} min ago"
    elif time_difference < timedelta(days=1):
        hours = int(time_difference.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        return email_time.strftime("%d %b %Y %H:%M:%S")

if __name__ == '__main__':
    app.run(debug=True,port=5008)