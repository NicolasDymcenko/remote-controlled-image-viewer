from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required
from flask import request
from .models import PaketBild
from . import db, socketio
import base64

from .events import connected_ips

# Auth API for login (no protection)
auth_api = Namespace('auth', description='Authentication operations')

# Define the model for login input
login_model = auth_api.model('Login', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The password')
})

@auth_api.route('/login')
@auth_api.doc(security=None, description="User login to get a JWT token. No authentication required for this endpoint.")
class Login(Resource):
    @auth_api.expect(login_model)
    def post(self):
        """
        Handle user login and return a JWT token if the credentials are valid.
        """
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Replace this with your own authentication logic
        if username == 'testuser' and password == 'testpassword':  # Example credentials
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}, 200
        else:
            return {'message': 'Invalid credentials'}, 401


# PaketBild API namespace with default JWT protection
api = Namespace(
    'paketbilder',
    description='Paket Bild related operations',
    decorators=[jwt_required()],  # Apply jwt_required to all routes in this namespace
    security='jwt'  # Add JWT security for Swagger documentation
)

# Route to send images to a specific IP
@api.route('/<string:paket_id>/<string:ip>')
@api.response(404, 'Paket ID not found')
@api.response(400, 'IP not connected to WebSocket')
@api.doc(description="Send images to a specific IP connected via WebSocket. Requires a valid JWT token.")
class PaketBildList(Resource):
    def get(self, paket_id, ip):
        """
        Get all PaketBild entries with the same paket_id, and send the image data via WebSocket to a specific IP room.
        """
        if ip not in connected_ips:
            return {'error': f'IP {ip} is not connected to WebSocket.'}, 400

        # Query the database and order by 'ausschnitt' (True first)
        paket_bilder = PaketBild.query.filter_by(paket_id=paket_id).order_by(PaketBild.ausschnitt.desc()).all()

        if not paket_bilder:
            api.abort(404, f'Paket ID {paket_id} not found')

        # Convert binary 'paket_bild' data to Base64
        image_data = [base64.b64encode(bild.paket_bild).decode('utf-8') for bild in paket_bilder]

        # Emit image data to the specific room (identified by IP)
        socketio.emit('newImage', image_data, room=ip)

        return f'Images sent to IP: {ip} via WebSocket', 200


# Route to view all connected IPs
@api.route('/connected_ips')
@api.doc(description="View all currently connected IP addresses. Requires a valid JWT token.")
class ConnectedIPs(Resource):
    def get(self):
        """
        Return a list of all currently connected IP addresses.
        """
        return {'connected_ips': list(connected_ips)}, 200


# Route to clear all images for a specific IP (without deleting data)
@api.route('/clear_images/<string:ip>')
@api.response(400, 'IP not connected to WebSocket')
@api.doc(description="Clear all displayed images for a specific IP via WebSocket. Requires a valid JWT token.")
class ClearImagesForIP(Resource):
    def post(self, ip):
        """
        Send a WebSocket event to clear all displayed images for a specific IP.
        """
        if ip not in connected_ips:
            return {'error': f'IP {ip} is not connected to WebSocket.'}, 400

        # Emit a 'clearImages' event to the specific IP room
        socketio.emit('clearImages', room=ip)

        return f'Clear images event sent to IP: {ip}', 200
