import React, { useState } from 'react';
import './App.css';
import FileUpload from './FileUpload';
import ChatInterface from './ChatInterface';
import IntroModal from './IntroModal'; // Import your new modal component

function App() {
  // State to manage modal visibility
  const [isModalVisible, setModalVisible] = useState(true);

  // Function to hide the modal
  const closeModal = () => {
    setModalVisible(false);
  };

  return (
    <div className="App">
      {/* Render the modal component and pass the state and function as props */}
      <IntroModal isVisible={isModalVisible} onClose={closeModal} />

      <div className="main-container">
        <FileUpload />
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
