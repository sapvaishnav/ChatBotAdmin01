from flask import Flask

def create_app(config=None):
    # Use relative paths for template and static folders
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a secure key

    from app.routes import routes
    app.register_blueprint(routes)

    return app
