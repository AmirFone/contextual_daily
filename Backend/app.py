from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_cognito_auth import CognitoAuthManager, login_required
import os
from Audio_processing import split_audio, transcribe_audio
from Embedding_and_vector_database import upload_embeddings_to_db
from dotenv import load_dotenv

# Initialize the Flask application
app = Flask(__name__, static_url_path='')
load_dotenv()

# Configuration using environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
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
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Splitting and transcribing
        audio_segments = split_audio(filepath)
        transcriptions = transcribe_audio(audio_segments)
        upload_embeddings_to_db(transcriptions, session.get('cognito_user_id', 'none'))

        return jsonify(transcriptions=transcriptions), 200

    return jsonify(error='File upload failed'), 500

@app.route('/chatbox_query', methods=['POST'])
@login_required
def chatbox_query():
    query = request.json.get('query', '')
    # Placeholder for chat query handling logic
    # response = handle_chat_query(query)
    # return jsonify(response=response)
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
