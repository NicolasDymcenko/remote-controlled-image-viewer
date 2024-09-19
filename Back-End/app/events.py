from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

socketio = SocketIO(cors_allowed_origins="*")
connected_ips = set()

def get_client_ip():
    """Retrieve the client's IP address, accounting for proxies."""
    # Check for 'X-Forwarded-For' header, which is set by proxies
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]  # Return the first IP in the list
    else:
        return request.remote_addr  # Fallback to request.remote_addr if no proxy is involved

@socketio.on('connect')
def handle_connect():
    client_ip = get_client_ip()  # Get the client's real IP address
    connected_ips.add(client_ip)  # Add IP to connected set
    join_room(client_ip)  # Add the client to a room based on their IP
    print(f'Client connected with IP: {client_ip}, joined room: {client_ip}')
    emit('message', f'Willkommen {client_ip}, Sie sind jetzt verbunden!', room=client_ip)

@socketio.on('disconnect')
def handle_disconnect():
    client_ip = get_client_ip()  # Get the client's real IP address
    connected_ips.discard(client_ip)  # Remove IP from connected set
    leave_room(client_ip)  # Remove the client from their IP room
    print(f'Client disconnected: {client_ip}')
