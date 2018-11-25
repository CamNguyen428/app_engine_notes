import datetime

from flask import Flask, render_template, request, jsonify
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token

datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

app = Flask(__name__)

def fetch_notes(email):
    ancestor = datastore_client.key("User", email)
    query = datastore_client.query(kind='notes', ancestor=ancestor)
    query.order = ['-timestamp']
    notes = query.fetch()
    return notes

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    notes = [] 

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            notes = fetch_notes(claims['email'])
        except ValueError as exc:
            error_message = str(exc)
    return render_template('index.html', user_data=claims, notes=notes)

@app.route('/notes', methods=['POST'])
def create_note():
    id_token = request.cookies.get("token")
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            entity = datastore.Entity(key=datastore_client.key("User", claims['email'], 'notes'))
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

@app.route('/notes', methods=['GET'])
def retrieve_notes():
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    notes = fetch_notes(claims['email'])
    response = {
        'status': 200,
        'notes': list(map(lambda x: x['note'], notes))
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
