from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

# db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # db.init_app(app)
    # Migrate(app, db)

    from .routes import register_routes
    register_routes(app)

    return app
