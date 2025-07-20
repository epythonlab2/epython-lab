from flask import Blueprint

from . import main
from .dashboard import bp as dashboard_bp
from .tutorials import bp as tutorial_bp
from .audit_route import bp as audit_bp
from .analytics import bp as analytics_bp

def register_routes(app):
    app.register_blueprint(main.bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tutorial_bp, url_prefix='/api/v1/topics')
    app.register_blueprint(audit_bp, url_prefix="/api/v1/audit")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
