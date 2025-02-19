from flask import Flask
from app.database import init_db
from app.routes import routes

def create_app():
    """Creates and configures the Flask app"""
    app = Flask(__name__)

    # Initialize the database
    init_db()

    # Register the routes
    app.register_blueprint(routes)

    return app
