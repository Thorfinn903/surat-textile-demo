from ..extensions import socketio
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from flask import request, current_app

@socketio.on('connect')
def handle_connect():
    current_app.logger.info(f"SocketIO Client Connected: {request.sid}")
    emit('server_message', {'data': 'Connected to Digital Dukan Real-time Gateway'})

@socketio.on('disconnect')
def handle_disconnect():
    current_app.logger.info(f"SocketIO Client Disconnected: {request.sid}")

@socketio.on('join_admin_room')
def on_join_admin():
    if current_user.is_authenticated and current_user.role in ['admin', 'sales']:
        join_room('admin_room')
        current_app.logger.info(f"User {current_user.username} joined admin_room")
        emit('join_status', {'status': 'success', 'msg': 'Joined admin room'})
    else:
        current_app.logger.warning(f"Unauthorized admin room join attempt: {request.sid}")
        emit('join_status', {'status': 'error', 'msg': 'Unauthorized'}, to=request.sid)

@socketio.on('join_inquiry_room')
def on_join(data):
    room = data['product_id']
    join_room(room)
    emit('status', {'msg': f'User joined inquiry room for product {room}'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    """Placeholder for future real-time chat between buyer and seller."""
    room = data['product_id']
    message = data['message']
    emit('new_message', {'user': 'Buyer', 'text': message}, room=room)
