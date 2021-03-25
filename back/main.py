import uuid
import threading
import time
from requests import post

from flask import Flask, make_response, jsonify, request, current_app, session, url_for
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask_cors import CORS

from random import randint

app = Flask(__name__)
app.clients = {}
CORS(app)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app, cors_allowed_origins="*")


def thread_function(room, url, **kwargs):
    for i in range(10):
        time.sleep(1)
        post(url, json={'room': room})


@app.route('/clients', methods=['GET'])
def clients():
    print(app.clients)
    return make_response(jsonify({'clients': list(app.clients.keys())}))


@app.route('/job', methods=['POST'])
def job():
    userid = request.json['user_id']
    room = f'uid-{userid}'
    threading.Thread(target=thread_function, args=(
        room, url_for('status', _external=True, _method='POST'))).start()

    return make_response(jsonify({'x': 1}))


@app.route('/status', methods=['POST'])
def status():
    room = request.json['room']
    emit('status', {'key': 'value'}, room=room, namespace='/')

    return jsonify({})


@socketio.on('connect')
def connect():
    userid = str(uuid.uuid4())
    session['userid'] = userid
    print(request.namespace)
    current_app.clients[userid] = request.namespace
    print('Client connected! Assigned user id', userid)
    room = f'uid-{userid}'
    print('Room', room)
    join_room(room)
    emit('connected', {'user_id': userid})


@socketio.on('disconnect request')
def disconnect_request():
    emit('status', {'status': 'Disconnected!'})
    disconnect()


@socketio.on('disconnect')
def events_disconnect():
    del current_app.clients[session['userid']]
    room = f'uid-{userid}'
    leave_room(room)
    print('Client %s disconnected' % session['userid'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
