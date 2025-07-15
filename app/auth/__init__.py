from flask import Blueprint

from . user_routes import auth_bp

def register_auth_routes(app):
     app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
