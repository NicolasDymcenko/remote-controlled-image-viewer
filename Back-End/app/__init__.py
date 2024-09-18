from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('app.config.Config')
    
    # Initialize Flask extensions
    db.init_app(app)
    
    # Enable CORS for all domains (wildcard *)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Create the API
    api = Api(app, version='1.0', title='Simple API',
              description='A simple Flask RESTx API')
    
    # Import and register blueprints or namespaces
    from .routes import api as api_namespace
    api.add_namespace(api_namespace, path='/api')
    
    return app
