import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+psycopg://knownerror:akdv@192.168.2.248/paketbilder')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('MY_SECRET_KEY', 'testkey') # Secret key for JWT
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # Set token expiration to 24 hours (in seconds)
