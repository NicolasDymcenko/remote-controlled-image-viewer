from flask_restx import Namespace, Resource
from .models import PaketBild
from . import db
import base64

api = Namespace('paketbilder', description='Paket Bild related operations')

@api.route('/<string:paket_id>')
@api.response(404, 'Paket ID not found')
class PaketBildList(Resource):
    def get(self, paket_id):
        """
        Get all PaketBild entries with the same paket_id,
        ordered by ausschnitt (True first, then False),
        and return only the paket_bild data in Base64 format in an array.
        """
        # Query the database and order by 'ausschnitt', with True first
        paket_bilder = PaketBild.query.filter_by(paket_id=paket_id).order_by(PaketBild.ausschnitt.desc()).all()
        
        if not paket_bilder:
            api.abort(404, f'Paket ID {paket_id} not found')

        # Convert binary 'paket_bild' data to Base64 and return it in an array
        return [base64.b64encode(bild.paket_bild).decode('utf-8') for bild in paket_bilder]
