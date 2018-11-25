import datetime

from flask import Flask, render_template, request, jsonify
from google.cloud import datastore
from google.auth.transport import requests

datastore_client = datastore.Client()

app = Flask(__name__)

def fetch_notes():
    query = datastore_client.query(kind='notes')
    query.order = ['-timestamp']
    notes = query.fetch()
    return notes

@app.route('/')
def root():
    error_message = None
    notes = [] 

    try:
        notes = fetch_notes()
    except ValueError as exc:
        error_message = str(exc)

    return render_template('index.html', notes=notes)

@app.route('/notes', methods=['POST'])
def create_note():
    try:
        entity = datastore.Entity(key=datastore_client.key('notes'))
        entity.update({
            'note': request.json.get("note"),
            'timestamp': datetime.datetime.now()
        })
        datastore_client.put(entity)
    except ValueError as exc:
        error_message = str(exc)
    response = {
        'status': 200,
        'note': request.json.get("note")
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
