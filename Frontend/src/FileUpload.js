import React, { useState } from 'react';
import Modal from 'react-modal';
import './FileUpload.css';

// Set the root for the modal for accessibility reasons (usually your app's root div ID)
Modal.setAppElement('#root');

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [modalIsOpen, setModalIsOpen] = useState(false);

  const cognitoLoginUrl = "https://contextual.auth.us-east-1.amazoncognito.com/login?client_id=kfjm29snmd1vd04t7fjbf874s&response_type=code&scope=email+openid+phone&redirect_uri=http%3A%2F%2Flocalhost%3A3001%2F"; // actual Cognito URL

  const handleFileChange = (event) => {
    // Store the file
    setSelectedFile(event.target.files[0]);
    // Open the login modal
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    // If needed, handle the login confirmation logic here
  };

  const handleFileUpload = async () => {
    // Ensure the user has selected a file and closed the modal (meaning they're logged in)
    if (selectedFile && !modalIsOpen) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Example POST request to an API endpoint
      try {
        const response = await fetch('your-api-endpoint', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          setTranscript(result.transcript); // Update the transcript state with the response
        } else {
          console.error('Error uploading file');
        }
      } catch (error) {
        console.error('Error uploading file', error);
      }
    }
  };

  return (
    <div className="upload-container">
      <h1>File Upload Feature</h1>
      <div className="upload-box">
        <div className="title">Upload today's audio file</div>
        <div className="subtitle">Acceptable Formats: MP3, up to 50MB</div>
        <div className="subtitle">Also Acceptable: PDF, up to 50MB</div>
        <input
          id="file-upload"
          type="file"
          accept=".mp3, .pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-upload" className="upload-btn">
          Browse File
        </label>
        <button onClick={handleFileUpload} className="upload-btn">
          Upload
        </button>
      </div>
      {transcript && (
        <div className="transcript-container">
          <h2>Transcript</h2>
          <p>{transcript}</p>
        </div>
      )}
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Cognito Login"
        className="modal-content"
        overlayClassName="modal-overlay"
      >
        <iframe src={cognitoLoginUrl} title="Cognito Login" frameBorder="0" width="100%" height="100%"></iframe>
      </Modal>
    </div>
  );
};

export default FileUpload;
