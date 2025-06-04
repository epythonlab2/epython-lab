from flask import Blueprint

from . import main
from .dashboard import bp as dashboard_bp

def register_routes(app):
    app.register_blueprint(main.bp)
    app.register_blueprint(dashboard_bp)
