from flask import Flask
from config import get_config
from routes import register_routes

def create_app():
    app = Flask(__name__, static_url_path='')
    app.config.update(get_config())

    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
