from flask import Flask, render_template, request
import yaml

app = Flask(__name__)
#golabal variable
intent_global = ""
action_global = ""

@app.route('/')
def index():
    return render_template('modfier.html')



def add_intent(IN, EX):
    # Load NLU data
    with open('nlu.yml', 'r') as f:
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
        with open('nlu.yml', 'w') as f:
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
    with open('../domain.yml', 'r') as f:
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
    with open('../domain.yml', 'w') as f:
        f.writelines(lines)

    return "Response text updated successfully!"







@app.route('/add_data', methods=['POST'])
def handle_add_data():
    intent_name = request.form['intent_name']
    examples = request.form['new_examples']
    rep_name = request.form['resp_name']
    rep_text=request.form['resp_text']

    add_intent_result = add_intent(intent_name, examples)
    add_rep_result=update_response_text(rep_name,rep_text)



    # Concatenate all the results into a single response
    response = f"{add_intent_result},{add_rep_result}"

    return response


if __name__ == '__main__':
    app.run(debug=True,port=5009)