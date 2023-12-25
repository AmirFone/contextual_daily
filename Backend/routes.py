from flask import (
    Blueprint,
    jsonify,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    current_app as app,

)
from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt
from flask_cognito_auth import CognitoAuthManager
from werkzeug.utils import secure_filename
import os
import secrets
from Audio_processing import split_audio, transcribe_audio
from Embedding_and_vector_database import upload_embeddings_to_db, get_closest_documents
from pdf_processing import extract_text_and_process
from flask_uploader import Uploader
import glob
import requests
from jose import jwt

audio_bp = Blueprint("audio", __name__)
pdf_bp = Blueprint("pdf", __name__)
auth_bp = Blueprint("auth", __name__)
chat_bp = Blueprint("chat", __name__)
static_bp = Blueprint("static", __name__)

@static_bp.route("/<path:filename>")
def staticfiles(filename):
    return send_from_directory("static", filename)

@audio_bp.route("/upload", methods=["POST"])
@cognito_auth_required
def upload_audio():
        uploader = Uploader(app,None)
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
@cognito_auth_required
def upload_pdf():
        uploader = Uploader(app,None)
        # PDF upload logic
        if "pdf_file" not in request.files:
            return jsonify(error="No PDF file part"), 400
        file = request.files["pdf_file"]
        if file.filename == "":
            return jsonify(error="No selected file"), 400
        if file and uploader.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOADER_FOLDER"], filename)
            uploader.save(file, folder=app.config["UPLOADER_FOLDER"], name=filename)
            Parsed_text_dictionary = extract_text_and_process(filepath)
            upload_embeddings_to_db(
                Parsed_text_dictionary, session.get("cognito_user_id", "none")
            )
            os.remove(filepath)
            return jsonify(message="PDF uploaded successfully", filename=filename), 200
        return jsonify(error="File upload failed"), 500

@auth_bp.route("/callback", methods=["GET"])
def cognito_callback():
        id_token = request.args.get("id_token")

        if id_token:
            # Get the JSON Web Key Set (JWKS) from Cognito
            jwks_url = f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}/.well-known/jwks.json"
            jwks = requests.get(jwks_url).json()

            # Decode and verify the ID token
            try:
                # The following line assumes RS256 algorithm; adjust as needed based on your Cognito settings
                decoded_token = jwt.decode(id_token, jwks, algorithms=["RS256"])
                session["cognito_user_id"] = decoded_token["sub"]
            except jwt.JWTError:
                return "Invalid token", 401
        return redirect(url_for("main"))


@auth_bp.route("/login", methods=["GET"])
def login():
        # Generate a unique state value for CSRF protection
        state = secrets.token_urlsafe()
        session["oauth_state"] = state

        # Construct the Cognito login URL
        cognito_login_url = (
            f"https://{app.config['COGNITO_DOMAIN']}/login"
            f"?response_type=code"
            f"&client_id={app.config['COGNITO_CLIENT_ID']}"
            f"&redirect_uri={app.config['COGNITO_REDIRECT_URI']}"
            f"&state={state}"
        )

        # Redirect the user to the Cognito login URL
        return redirect(cognito_login_url)

@auth_bp.route("/logout", methods=["GET"])
@cognito_auth_required
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
    cognito_auth = CognitoAuthManager(app)
    app.register_blueprint(audio_bp, url_prefix="/audio")
    app.register_blueprint(pdf_bp, url_prefix="/pdf")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chat_bp, url_prefix="/chat")  # Register chat blueprint
    app.register_blueprint(static_bp)  # Register static blueprint
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



