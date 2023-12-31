from flask import Flask
from config import get_config
from routes import register_routes
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_url_path="")
    CORS(app)
    app.config.update(get_config())
    register_routes(app)
    return app

app = create_app()

def lambda_handler(event, context):
    # Logic to handle the Lambda event and return a response
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
