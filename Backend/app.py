from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_uploader import Uploader
from werkzeug.utils import secure_filename
from flask_cognito_auth import CognitoAuthManager, login_required
import os
import secrets
from Audio_processing import split_audio, transcribe_audio
from Embedding_and_vector_database import upload_embeddings_to_db, get_closest_documents
from pdf_processing import extract_text_and_process
from dotenv import load_dotenv 

# Initialize the Flask application
app = Flask(__name__, static_url_path='')
load_dotenv()
uploader = Uploader(app)
# PDF Uploader Configuration
upload_folder = os.path.join(os.getcwd(), 'upload')
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
app.config['UPLOADER_FOLDER'] = upload_folder  # Upload folder
app.config['UPLOADER_ALLOWED_EXTENSIONS'] = ['pdf']  # Allowed file types
app.config['UPLOADER_MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max file size

# Configuration using environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)) # Fallback to 50MB if not set

# AWS Cognito Configuration
app.config['COGNITO_REGION'] = os.getenv('COGNITO_REGION')
app.config['COGNITO_USER_POOL_ID'] = os.getenv('COGNITO_USER_POOL_ID')
app.config['COGNITO_CLIENT_ID'] = os.getenv('COGNITO_CLIENT_ID')
app.config['COGNITO_CLIENT_SECRET'] = os.getenv('COGNITO_CLIENT_SECRET')
app.config['COGNITO_DOMAIN'] = os.getenv('COGNITO_DOMAIN')
app.config['COGNITO_REDIRECT_URI'] = os.getenv('COGNITO_REDIRECT_URI')
app.config['COGNITO_SIGNOUT_URI'] = os.getenv('COGNITO_SIGNOUT_URI')
app.config['ERROR_REDIRECT_URI'] = os.getenv('ERROR_REDIRECT_URI')

cognito_auth = CognitoAuthManager(app)

# Generate a new state value for the OAuth2 request
def generate_state_value():
    state = secrets.token_urlsafe()
    session['oauth_state'] = state
    return state

cognito_auth = CognitoAuthManager(app)



@app.route('/login', methods=['GET'])
def login():
    return redirect(url_for('cognitologin'))

@app.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('cognitologout'))

@app.route('/cognito/login', methods=['GET'])
@login_required
def cognitologin():
    pass

@app.route('/cognito/callback', methods=['GET'])
@login_required
def cognito_callback():
    return redirect(url_for('home'))

@app.route('/cognito/logout', methods=['GET'])
@login_required
def cognitologout():
    pass

@app.route('/error')
def error():
    return jsonify({'Error': 'Something went wrong'}), 500

@app.route('/home')
@login_required
def home():
    return jsonify({'logged_in_as': session.get('username', 'none')}), 200

@app.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    if 'audio_file' not in request.files:
        return jsonify(error='No audio file part'), 400
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify(error='No selected file'), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Stream the file to disk
    file.save(filepath)

    try:
        # Process the audio file in chunks
        full_transcript = split_audio(filepath)
        # Process the transcript
        transcriptions = transcribe_audio(full_transcript)

        # Upload embeddings to the database
        upload_embeddings_to_db(transcriptions, session.get('cognito_user_id', 'none'))

        # Clean up: Delete the original audio file and any generated segments
        os.remove(filepath)
        for segment_file in glob.glob(f"{filepath}_part*.wav"):
            os.remove(segment_file)

        return jsonify(transcriptions=transcriptions), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    if 'pdf_file' not in request.files:
        return jsonify(error='No PDF file part'), 400

    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify(error='No selected file'), 400

    if file and uploader.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOADER_FOLDER'], filename)

        # Save file in chunks to handle large files
        uploader.save(file, folder=app.config['UPLOADER_FOLDER'], name=filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result = extract_text_and_process(file_path)
        os.remove(file_path)
        # Additional processing can be done here

        return jsonify(message='PDF uploaded successfully', filename=filename), 200

    return jsonify(error='File upload failed'), 500

@app.route('/chatbox_query', methods=['POST'])
@login_required
def chatbox_query():
    query = request.json.get('query', '')
    get_closest_documents(session.get('cognito_user_id', 'none'), query)
    
    return jsonify(response='Chat query received', query=query)

# Static file handling
@app.route('/static/<path:filename>')
def staticfiles(filename):
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

@app.errorhandler(500)
def internal_server_error(error):
    return 'Internal server error', 500

# Main block to run the app
if __name__ == '__main__':
    app.run(debug=True)
