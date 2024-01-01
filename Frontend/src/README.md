Contextual Chat for Document Analysis
Overview
This web application provides a platform to upload and analyze large documents and audio files. Utilizing advanced semantic analysis and a Flask backend, the app converts uploaded content into embeddings and stores them in a vector database. Users can interact with the system via a chat interface that contextualizes conversations by comparing chat query embeddings with document vectors.

Features
Upload PDF documents and audio files (MP3, M4A)
Backend processing of files to extract text and audio transcriptions
Embedding generation and upload to vector database for semantic analysis
Chat interface to query and retrieve contextual information from uploaded content
Cognito authentication for secure user sessions
Frontend Components
FileUpload: Component for uploading documents and audio files with progress indication
ChatInterface: A chat system for interacting with the backend, providing contextual responses based on the uploaded content
IntroModal: An introductory modal that provides users with information about the app's capabilities
Backend Services
audio: Handles audio file uploads and processing
pdf: Manages PDF file uploads and text extraction
auth: Cognito-based authentication system for user management
chat: Chat service that processes queries and returns contextual responses
static: Serves static files
login/logout: Cognito-based login and logout flow
Installation
Clone the repository.
Install dependencies using npm install for frontend and pip install -r requirements.txt for backend.
Set up environment variables for AWS and OpenAI credentials.
Configure Cognito authentication according to your AWS user pool.
Start the Flask backend server.
Launch the React frontend.
Usage
Log in with Cognito to start a session.
Upload a file using the FileUpload component.
Navigate to the ChatInterface to start a contextual conversation based on the uploaded content.
Use the IntroModal for guided instructions on using the application.
Contributing
Feedback and contributions are welcome. Please feel free to fork the repository and submit pull requests.

Support
If you encounter any issues or have questions, please email support@example.com.

License
This project is licensed under the MIT License - see the LICENSE.md file for details.

