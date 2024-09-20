# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
from .events import socketio

def create_app():
    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_object('app.config.Config')

    # Initialize Flask extensions
    db.init_app(app)

    # Initialize JWT Manager
    jwt = JWTManager(app)

    # Enable CORS for all domains
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Define JWT security scheme for Swagger
    authorizations = {
        'jwt': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT token for authorization. Format: Bearer {token}'
        }
    }

    # Create the API with JWT security
    api = Api(app, version='1.0', title='Simple API',
              description='A simple Flask RESTx API',
              security='jwt',
              authorizations=authorizations)

    # Import and register blueprints or namespaces
    from .routes import api as api_namespace, auth_api
    api.add_namespace(api_namespace, path='/api')
    api.add_namespace(auth_api, path='/auth')  # Add the auth namespace

    # Initialize SocketIO with the Flask app
    socketio.init_app(app)

    # JWT error handling (optional but recommended)
    @jwt.expired_token_loader
    def expired_token_callback(expired_token):
        return {'message': 'The token has expired.'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return {'message': f'Invalid token: {reason}'}, 401

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return {'message': 'Missing or invalid token.'}, 401

    return app
