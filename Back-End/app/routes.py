from flask_restx import Namespace, Resource
from .models import PaketBild
from . import db, socketio
import base64

api = Namespace('paketbilder', description='Paket Bild related operations')

from .events import connected_ips

# Route to send images to a specific IP
@api.route('/<string:paket_id>/<string:ip>')
@api.response(404, 'Paket ID not found')
class PaketBildList(Resource):
    def get(self, paket_id, ip):
        """
        Get all PaketBild entries with the same paket_id,
        ordered by ausschnitt (True first, then False),
        and send the image data via WebSocket to a specific IP room.
        """
        # Query the database and order by 'ausschnitt', with True first
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
class ConnectedIPs(Resource):
    def get(self):
        """
        Return a list of all currently connected IP addresses.
        """
        return {'connected_ips': list(connected_ips)}, 200

# Route to clear all images for a specific IP (without deleting data)
@api.route('/clear_images/<string:ip>')
class ClearImagesForIP(Resource):
    def post(self, ip):
        """
        Send a WebSocket event to the specific IP room to clear all displayed images.
        """
        # Check if the IP is connected
        if ip not in connected_ips:
            return {'error': f'IP {ip} is not connected.'}, 404

        # Emit a 'clearImages' event to the specific IP room
        socketio.emit('clearImages', room=ip)

        return f'Clear images event sent to IP: {ip}', 200
