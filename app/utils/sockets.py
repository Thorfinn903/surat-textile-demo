from ..extensions import socketio
from flask_socketio import emit, join_room, leave_room

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('server_message', {'data': 'Connected to Surat Textile Nexus Real-time Gateway'})

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
