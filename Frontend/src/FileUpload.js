// FileUpload.js
import React, { useState } from 'react';
import './FileUpload.css'; // Make sure the path to your CSS file is correct

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  // This function is called when the file input changes (file is selected)
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // This function is called when the upload button is clicked
  const handleFileUpload = () => {
    if (selectedFile) {
      console.log(selectedFile);
      // Here, you would typically handle the file upload process,
      // e.g., sending the file to a backend server
    } else {
      console.log('No file selected');
    }
  };

  return (
    <div className="file-upload-container">
      <label htmlFor="file-upload" className="upload-btn">
        Choose File
      </label>
      <input
        id="file-upload"
        type="file"
        className="file-input"
        onChange={handleFileChange}
      />
      <button onClick={handleFileUpload} className="upload-btn">
        Upload File
      </button>
    </div>
  );
};

export default FileUpload;
