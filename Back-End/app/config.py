import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+psycopg://knownerror:akdv@192.168.2.248/paketbilder')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
