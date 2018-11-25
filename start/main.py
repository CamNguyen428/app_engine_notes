from flask import Flask, render_template, request, jsonify
from google.auth.transport import requests

app = Flask(__name__)

@app.route('/')
def root():
    error_message = None
    notes = [ {'note': 'sample note'}, {'note': 'second sample'} ]

    return render_template('index.html', notes=notes)

@app.route('/notes', methods=['POST'])
def create_note():
    # Send the note back in response
    response = {
        'status': 200,
        'note': request.json.get("note")
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
