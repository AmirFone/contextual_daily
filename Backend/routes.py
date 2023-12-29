from flask import (
    Blueprint,
    jsonify,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    current_app as app,
    make_response,

)
from functools import wraps
# from flask_cognito import cognito_auth_required, CognitoAuth

# from flask_cognito_auth import CognitoAuthManager
from werkzeug.utils import secure_filename
import os
import secrets
from Audio_processing import split_audio, transcribe_audio
from Embedding_and_vector_database import upload_embeddings_to_db, get_closest_documents
from pdf_processing import extract_text_and_process
from flask_uploader import Uploader
import glob
import requests
import urllib.parse
import base64
import cognitojwt
audio_bp = Blueprint("audio", __name__)
pdf_bp = Blueprint("pdf", __name__)
auth_bp = Blueprint("auth", __name__)
chat_bp = Blueprint("chat", __name__)
static_bp = Blueprint("static", __name__)
login_bp = Blueprint("login", __name__)
loginout_bp = Blueprint("logout", __name__)
@static_bp.route("/<path:filename>")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "cognito_user_id" not in session:
            # Redirect to login or return an unauthorized error
            print('login:', session)
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

def staticfiles(filename):
    return send_from_directory("static", filename)

@audio_bp.route("/upload", methods=["POST"])
@login_required
def upload_audio():
        # Audio upload logic
        if "audio_file" not in request.files:
            return jsonify(error="No audio file part"), 400
        file = request.files["audio_file"]
        if file.filename == "":
            return jsonify(error="No selected file"), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        try:
            full_transcript = split_audio(filepath)
            transcriptions = transcribe_audio(full_transcript)
            upload_embeddings_to_db(
                transcriptions, session.get("cognito_user_id", "none")
            )
            os.remove(filepath)
            for segment_file in glob.glob(f"{filepath}_part*.wav"):
                os.remove(segment_file)
            return jsonify(transcriptions=transcriptions), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

@pdf_bp.route("/upload", methods=["POST"])
@login_required
def upload_pdf():
    print("Starting PDF upload process")
    uploader = app.uploader

    if "pdf_file" not in request.files:
        print("Error: No PDF file part in request.files")
        return jsonify(error="No PDF file part"), 400

    file = request.files["pdf_file"]

    if file.filename == "":
        print("Error: No file selected")
        return jsonify(error="No selected file"), 400

    if file and uploader.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOADER_FOLDER"], filename)
        print(f"Saving file: {filepath}")
        uploader.save(file, folder=app.config["UPLOADER_FOLDER"], name=filename)

        print("Extracting text from PDF and processing")
        Parsed_text_dictionary = extract_text_and_process(filepath)

        print("Uploading embeddings to database")
        upload_embeddings_to_db(
            Parsed_text_dictionary, session.get("cognito_user_id", "none")
        )

        print("Removing uploaded file")
        os.remove(filepath)

        print("PDF uploaded successfully")
        return jsonify(message="PDF uploaded successfully", filename=filename), 200

    print("Error: File upload failed")
    return jsonify(error="File upload failed"), 500


@auth_bp.route("/callback", methods=["GET"])
def cognito_callback():
    auth_code = request.args.get("code")
    # print('Authorization code:', auth_code, ",", request)

    if auth_code:
        token_url = "https://contextual.auth.us-east-1.amazoncognito.com/oauth2/token"
        # print('Token URL:', token_url)
        # Client secret handling (if your app client has a secret)
        client_auth = f"{app.config['COGNITO_CLIENT_ID']}:{app.config['COGNITO_CLIENT_SECRET']}"
        client_auth = bytes(f"{app.config['COGNITO_CLIENT_ID']}:{app.config['COGNITO_CLIENT_SECRET']}",'utf-8')
        # encoded_client_auth = base64.b64encode(client_auth.encode()).decode()
        encoded_client_auth = base64.b64encode(client_auth).decode() 

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded_client_auth}'
        }

        data = {
            'grant_type': 'authorization_code',
            'client_id': app.config['COGNITO_CLIENT_ID'],
            'code': auth_code,
            'redirect_uri': app.config['COGNITO_REDIRECT_URI']
        }
        # print('Data:', data)
        # print('Headers:', headers)
        response = requests.post(token_url, headers=headers, data=urllib.parse.urlencode(data))

        if response.status_code == 200:
            tokens = response.json()
            id_token = tokens['id_token']
            # print('ID Token:', id_token)

            if id_token:
                try:
            # Replace these with your actual configuration values
                        REGION = app.config['COGNITO_REGION']
                        USERPOOL_ID = app.config['COGNITO_USER_POOL_ID']
                        APP_CLIENT_ID = app.config['COGNITO_CLIENT_ID']

            # Decode and verify the ID token
                        decoded_token = cognitojwt.decode(
                id_token,
                REGION,
                USERPOOL_ID,
                app_client_id=APP_CLIENT_ID
            )
                        # print('Decoded token:', decoded_token)
                        session["cognito_user_id"] = decoded_token["sub"]
                        print('session cognito_user_id:', session)


                except Exception as e:
                    # print(f"Error verifying token: {e}")
                    return "Invalid token", 401

        else:
            return f"Error fetching tokens: {response.content}", response.status_code
    response = make_response("", 302)
    response.headers["Location"] = 'https://192.168.86.34:3000'
    return response


@login_bp.route("/login", methods=["GET"])
def login():
    # Generate a unique state value for CSRF protection
    state = secrets.token_urlsafe()
    session["oauth_state"] = state

    # Ensure the redirect_uri is URL encoded
    encoded_redirect_uri = urllib.parse.quote_plus(app.config['COGNITO_REDIRECT_URI'])

    # Construct the Cognito login URL
    cognito_login_url = (
        f"{app.config['COGNITO_DOMAIN']}/login"
        f"?response_type=code"
        f"&client_id={app.config['COGNITO_CLIENT_ID']}"
        f"&redirect_uri={encoded_redirect_uri}"
        f"&state={state}"
    )

    # Redirect the user to the Cognito login URL
    # print(f'cognito_login_url {cognito_login_url}')
    return jsonify(url=cognito_login_url)

@loginout_bp.route("/logout", methods=["GET"])
@login_required
def logout():
        # Construct the Cognito logout URL
        cognito_logout_url = (
            f"https://{app.config['COGNITO_DOMAIN']}/logout"
            f"?client_id={app.config['COGNITO_CLIENT_ID']}"
            f"&logout_uri={url_for('auth_bp.login', _external=True)}"
        )

        # Redirect the user to the Cognito logout URL
        return redirect(cognito_logout_url)

def register_routes(app):
    # cognito_auth = CognitoAuthManager(app)
    # cognito_auth.init(app)
    # cogauth = CognitoAuth(app)
    uploader = Uploader(app,None)
    app.register_blueprint(audio_bp, url_prefix="/audio")
    app.register_blueprint(pdf_bp, url_prefix="/pdf")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chat_bp, url_prefix="/chat")  # Register chat blueprint
    app.register_blueprint(static_bp)  # Register static blueprint
    app.register_blueprint(login_bp, url_prefix="/login")
    # photos = UploadSet('photos', IMAGES)
    app.config["UPLOADER_FOLDER"] = app.config["UPLOAD_FOLDER"]
    app.config["UPLOADER_ALLOWED_EXTENSIONS"] = {"pdf"}
    app.config["UPLOADER_MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2GB
    def generate_state_value():
        state = secrets.token_urlsafe()
        session["oauth_state"] = state
        return state

    def chatbox_query():
        query = request.json.get("query", "")
        get_closest_documents(session.get("cognito_user_id", "none"), query)
        return jsonify(response="Chat query received", query=query)


    @app.errorhandler(404)
    def page_not_found(error):
        return "This page does not exist", 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return "Internal server error", 500

