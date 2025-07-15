# app/__init__.py

from flask import Flask, request, redirect
from flask_swagger_ui import get_swaggerui_blueprint

from app.extensions import db, migrate, jwt
from app.routes import register_routes
from app.auth import register_auth_routes
from app.cli import create_admin, seed_roles


def create_app():
    """
    Flask application factory.
    Initializes and configures the Flask app with extensions, blueprints, CLI commands, and JWT error handlers.
    """
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object("config.Config")

    # ----------------------------
    # Initialize Flask extensions
    # ----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ----------------------------
    # Register application routes
    # ----------------------------
    register_routes(app)
    register_auth_routes(app)

    # ----------------------------
    # Register Swagger UI for API docs
    # ----------------------------
    swaggerui_blueprint = get_swaggerui_blueprint(
        '/docs',                            # URL prefix for docs
        '/static/swagger.json',             # Path to the OpenAPI spec
        config={'app_name': "Tutorials API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix='/docs')

    # ----------------------------
    # Database setup
    # ----------------------------
    with app.app_context():
        db.create_all()

    # ----------------------------
    # Register custom CLI commands
    # ----------------------------
    app.cli.add_command(create_admin)
    app.cli.add_command(seed_roles)  # Add this line to register seed_roles

    # ----------------------------
    # JWT error handlers
    # ----------------------------
    @app.after_request
    def add_no_cache_headers(response):
        if request.path.startswith('/dcp/'):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
    
    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        """
        Handle missing JWT (e.g., missing cookie). Redirect to login for HTML requests.
        """
        if request.accept_mimetypes.accept_html:
            return redirect('/dcp/auth/login')
        return {"msg": reason}, 401

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        """
        Handle invalid JWT (e.g., malformed token). Redirect to login for HTML requests.
        """
        if request.accept_mimetypes.accept_html:
            return redirect('/dcp/auth/login')
        return {"msg": reason}, 401

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        """
        Handle expired JWTs. Redirect to login for HTML requests.
        """
        if request.accept_mimetypes.accept_html:
            return redirect('/dcp/auth/login')
        return {"msg": "Token has expired"}, 401

    return app
