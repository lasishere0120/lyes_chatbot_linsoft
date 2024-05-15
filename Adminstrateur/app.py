from flask import Flask, render_template, request
import yaml

app = Flask(__name__)
#golabal variable
intent_global = ""
action_global = ""

@app.route('/')
def index():
    return render_template('ajouter.html')

def intent_exists(intent_name, nlu_data):
        return intent_name in nlu_data

def add_intent(IN, EX):
        # Load NLU data
        with open('../nlu.yml', 'r') as f:
            nlu_data = f.read()

        # Check if intent already exists
        if intent_exists(IN, nlu_data):
            return "Intent already exists!"
        else:

           formatted_examples = ["    - " + example.strip() for example in EX.split('\n')]

           with open('../nlu.yml', 'a') as f:
            f.write(f"\n- intent: {IN}\n")
            f.write("  examples: |\n")
            f.write('\n'.join(formatted_examples) + '\n')

        return "Intent added successfully!"


def add_story(SN, I, A):
    with open('../stories.yml', 'r') as f:
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
    with open('../stories.yml', 'a') as f:
        f.write(new_story)

    return "Story added successfully!"

def add_response(IN, RN, RC):
    with open('../domain.yml', 'r') as f:
        lines = f.readlines()

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

    with open('../domain.yml', 'w') as f:
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
        f.writelines(lines[session_config_index:])  # Write the session_config block as it is

    return "Intent and response added successfully!"






@app.route('/add_data', methods=['POST'])
def handle_add_data():
    intent_name = request.form['name_intent']
    examples = request.form['examples']
    response_name = request.form['response_name']
    response_text = request.form['response_text']

    add_intent_result = add_intent(intent_name, examples)
    add_response_result = add_response(intent_name, response_name, response_text)

    story_name = "admin story"
    action_global = "utter_" + response_name
    intent_global = intent_name
    add_story_result = add_story(story_name, intent_global, action_global)

    # Concatenate all the results into a single response
    response = f"{add_intent_result}\n{add_response_result}\n{add_story_result}"

    return response


if __name__ == '__main__':
    app.run(debug=True,port=5001)