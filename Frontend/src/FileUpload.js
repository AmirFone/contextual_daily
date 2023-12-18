import React, { useState } from 'react';
import './FileUpload.css';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcript, setTranscript] = useState("");

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setTranscript(""); // Clear the previous transcript when a new file is selected
  };

  const handleFileUpload = async () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await fetch('your-api-endpoint', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          setTranscript(result.transcript); // Update the transcript state with the API response
        } else {
          console.error('Error uploading file');
        }
      } catch (error) {
        console.error('Error uploading file', error);
      }
    } else {
      console.log('No file selected');
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-box">
        <div className="title">upload today's audio file</div>
        <div className="subtitle">Acceptable Formats: MP3, up to 50MB</div>
        <label htmlFor="file-upload" className="upload-btn">
          Browse File
        </label>
        <input
          id="file-upload"
          type="file"
          onChange={handleFileChange}
        />
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
