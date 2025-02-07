from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from app.routes import routes  # Import routes
    app.register_blueprint(routes)  # Register routes

    return app
