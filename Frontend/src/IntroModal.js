// IntroModal.js
import React from 'react';
import './IntroModal.css';

const IntroModal = ({ isVisible, onClose }) => {
  const modalStyle = {
    display: isVisible ? 'block' : 'none',
  };

  return (
    <div className="modal" style={modalStyle}>
      <div className="modal-content">
        <span className="close" onClick={onClose}>&times;</span>
        <h2>Welcome to My Service!</h2>
        <p>I've developed this project to assist users in effectively navigating and understanding extensive documentations, such as PDFs, and unstructured data like large transcripts or audio recordings. By employing advanced semantic search and retrieval techniques, my service facilitates augmented data generation, providing meaningful insights.</p>
        <p>This product is particularly well-suited for documents that are longer than 30 pages, enabling efficient handling and analysis of substantial text volumes. To learn more about the technical aspects of this project, you can visit my <a href="https://github.com/amirfone" target="_blank">GitHub profile</a>.</p>
        <p><strong>Note:</strong> This platform is a <em>technical preview</em> developed solely by me and is not intended for production use. Leveraging large language models can be costly, hence, this service will be limited once it incurs an API cost of $20. This cost cap is implemented to manage expenses while offering a glimpse into the capabilities of this technology.</p>
        <p>Your interest and feedback are highly appreciated as I continue to develop and refine this innovative tool. If you have any questions or feedback, feel free to <a href="mailto:Ah2324@cornell.edu">Email me</a>.</p>
        {/* Add more content here as needed */}
      </div>
    </div>
  );
};

export default IntroModal;
