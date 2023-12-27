import React, { useState, useEffect } from 'react';
import './FileUpload.css';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcript, setTranscript] = useState("");

  // Added: useEffect to handle file upload after returning from sign-in
  useEffect(() => {
    // Check if there's a file reference in local storage after user returns from sign-in
    const savedFileData = localStorage.getItem('fileUpload');
    if (savedFileData) {
      const savedFile = JSON.parse(savedFileData);
      handleFileUpload(savedFile); // Continue with the upload
      localStorage.removeItem('fileUpload'); // Clear the saved file from local storage
    }
  }, []);

  // Modified: Saving file to state and local storage on file selection
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Save file metadata to local storage
    const fileData = {
      name: file.name,
      type: file.type,
      size: file.size
    };
    localStorage.setItem('fileUpload', JSON.stringify(fileData)); 

    // Existing login redirection logic...
    try {
      const response = await fetch("https://127.0.0.1:5000/login/login");
      if (response.ok) {
        const data = await response.json();
        const cognitoLoginUrl = data.url;
        window.location.href = cognitoLoginUrl;
      } else {
        console.error('Server responded with a non-OK status', response.status);
      }
    } catch (error) {
      console.error('Error during login redirection', error);
    }
  };

  // Modified: Accepting a file parameter for the upload process
  const handleFileUpload = async (file = selectedFile) => {
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      // Determine the endpoint based on file type
      let endpoint = '';
      if (file.type === 'application/pdf') {
        endpoint = 'https://127.0.0.1:5000/pdf/upload';
      } else if (file.type.startsWith('audio/')) {
        endpoint = 'https://127.0.0.1:5000/audio/upload';
      } else {
        console.error('Unsupported file type');
        return;
      }

      try {
        const response = await fetch(endpoint, {
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

  // Your existing JSX...
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
    </div>
  );
};

export default FileUpload;
