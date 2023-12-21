from flask import Blueprint, jsonify, request, redirect, url_for, session, send_from_directory
from flask_cognito_auth import CognitoAuthManager, login_required
from werkzeug.utils import secure_filename
import os
import secrets
from Audio_processing import split_audio, transcribe_audio
from Embedding_and_vector_database import upload_embeddings_to_db, get_closest_documents
from pdf_processing import extract_text_and_process
from flask_uploader import Uploader
import glob

audio_bp = Blueprint('audio', __name__)
pdf_bp = Blueprint('pdf', __name__)
auth_bp = Blueprint('auth', __name__)
chat_bp = Blueprint('chat', __name__)
static_bp = Blueprint('static', __name__)

def register_routes(app):
    cognito_auth = CognitoAuthManager(app)
    app.register_blueprint(audio_bp, url_prefix='/audio')
    app.register_blueprint(pdf_bp, url_prefix='/pdf')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')  # Register chat blueprint
    app.register_blueprint(static_bp)  # Register static blueprint

    uploader = Uploader(app)
    app.config['UPLOADER_FOLDER'] = app.config['UPLOAD_FOLDER']
    app.config['UPLOADER_ALLOWED_EXTENSIONS'] = ['pdf']
    app.config['UPLOADER_MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB
    
    def generate_state_value():
            state = secrets.token_urlsafe()
            session['oauth_state'] = state
            return state
    
    def chatbox_query():
        query = request.json.get('query', '')
        get_closest_documents(session.get('cognito_user_id', 'none'), query)
        return jsonify(response='Chat query received', query=query)

    @static_bp.route('/<path:filename>')
    def staticfiles(filename):
        return send_from_directory('static', filename)

    @app.errorhandler(404)
    def page_not_found(error):
        return 'This page does not exist', 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return 'Internal server error', 500

    @audio_bp.route('/upload', methods=['POST'])
    @login_required
    def upload_audio():
        # Audio upload logic
        if 'audio_file' not in request.files:
            return jsonify(error='No audio file part'), 400
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify(error='No selected file'), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            full_transcript = split_audio(filepath)
            transcriptions = transcribe_audio(full_transcript)
            upload_embeddings_to_db(transcriptions, session.get('cognito_user_id', 'none'))
            os.remove(filepath)
            for segment_file in glob.glob(f"{filepath}_part*.wav"):
                os.remove(segment_file)
            return jsonify(transcriptions=transcriptions), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    @pdf_bp.route('/upload', methods=['POST'])
    @login_required
    def upload_pdf():
        # PDF upload logic
        if 'pdf_file' not in request.files:
            return jsonify(error='No PDF file part'), 400
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify(error='No selected file'), 400
        if file and uploader.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOADER_FOLDER'], filename)
            uploader.save(file, folder=app.config['UPLOADER_FOLDER'], name=filename)
            Parsed_text_dictionary = extract_text_and_process(filepath)
            upload_embeddings_to_db(Parsed_text_dictionary, session.get('cognito_user_id', 'none'))
            os.remove(filepath)
            return jsonify(message='PDF uploaded successfully', filename=filename), 200
        return jsonify(error='File upload failed'), 500

    # Additional route handlers from your original code can be added here
    @auth_bp.route('/login', methods=['GET'])
    def login():
        # Login logic
        return redirect(url_for('cognitologin'))

    @auth_bp.route('/logout', methods=['GET'])
    @login_required
    def logout():
        # Logout logic
        return redirect(url_for('cognitologout'))

    # ... other auth related routes ...
