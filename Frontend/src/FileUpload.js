import React, { useState, useEffect } from 'react';
import './FileUpload.css';
import ProgressBar from 'react-bootstrap/ProgressBar';
const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [previousFileData, setPreviousFileData] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0); 
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const savedFileData = sessionStorage.getItem('fileUpload');
    if (savedFileData) {
      setPreviousFileData(JSON.parse(savedFileData)); // Set the previous file data
      // Prompt the user to reselect the file (implement UI logic as needed)
    }
  }, []);

  const simulateUploadProgress = async (fileSize) => {
    const uploadTimePerMB = 11; // Set this to the number of seconds per MB
    const totalUploadTime = fileSize * uploadTimePerMB;

    for (let i = 0; i <= 100; i++) {
      setUploadProgress(i);
      await new Promise(resolve => setTimeout(resolve, totalUploadTime * 10)); // Wait for a fraction of total upload time
    }
  };


  // Modified: Saving file to state and local storage on file selection
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log("Selected file type:", file.type);  // Add this line for debugging
      setSelectedFile(file);
    }
  };

  const handleFileUpload = async (file = selectedFile) => {
    if (file) {
      setIsLoading(true);
      setUploadProgress(0); // Reset progress
      const formData = new FormData();
      formData.append('pdf_file', file);
      const fileSizeMB = file.size / 1024 / 1024; // Convert size to MB
      await simulateUploadProgress(fileSizeMB);
      let uniqueUserId = localStorage.getItem("uniqueUserId");
      if (!uniqueUserId) {
        uniqueUserId = generateUniqueUserId();
        localStorage.setItem("uniqueUserId", uniqueUserId);
      }
      formData.append('unique_user_id', uniqueUserId);
  
      let endpoint = '';
      console.log("Uploaded file type:", file.type);
      if (file.type === 'application/pdf') {
        endpoint = 'https://contextual-9b9c45ec5823.herokuapp.com/pdf/upload';
      } else if (file.type.startsWith('audio/')) {
        endpoint = 'https://contextual-9b9c45ec5823.herokuapp.com/audio/upload';
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
          setTranscript(result.transcript);
        } else {
          console.error('Error uploading file');
        }
      } catch (error) {
        console.error('Error uploading file', error);
      }
      setIsLoading(false);
    }
  };

  function generateUniqueUserId() {
    return 'uid-' + Date.now().toString(36) + Math.random().toString(36).substr(2);
  }
  
  return (
    <div className="upload-container">
      <h1>Semantic Analysis Tool</h1>
      <div className="upload-box">
        <p>Enhance your documents and audio files with our advanced semantic analysis. Get started by uploading your file.</p>
        <div className="title">File Upload</div>
        <div className="subtitle">Supported Audio: MP3, M4A (Max 50MB)</div>
        <div className="subtitle">Supported Documents: PDF (Max 300 pages)</div>
        <input
          id="file-upload"
          type="file"
          accept=".mp3, .pdf, .m4a"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <div className="button-container">
          <label htmlFor="file-upload" className="upload-btn">Select File</label>
          <button onClick={() => handleFileUpload(selectedFile)} className="upload-btn">Start Analysis</button>
        </div>
      </div>

      {isLoading && (
        <ProgressBar
          now={uploadProgress}
          label={`${uploadProgress}%`}
          className="progress-bar"
          striped
          animated
        />
      )}

      {transcript && (
        <div className="transcript-container">
          <h2>Extracted Content</h2>
          <p>{transcript}</p>
        </div>
      )}

      {previousFileData && (
        <div className="reupload-notification">
          <p>You have a pending file. Please reselect: {previousFileData.name}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;