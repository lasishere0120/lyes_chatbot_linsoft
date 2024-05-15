from flask import Flask, render_template, request

app = Flask(__name__)

def remove_intent(intent_name):
    try:
        with open('nlu.yml', 'r') as f:
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
            with open('nlu.yml', 'w') as f:
                f.writelines(nlu_data)

            return f"Intent '{intent_name}' removed successfully!"
        else:
            return f"Intent '{intent_name}' not found!"
    except Exception as e:
        return f"Error removing intent: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove_intent', methods=['POST'])
def remove_intent_route():
    intent_name = request.form.get('intent_name')
    if intent_name:
        message = remove_intent(intent_name)
    else:
        message = "Please provide an intent name."
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
