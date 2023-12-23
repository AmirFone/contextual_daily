import React, { useState } from 'react';
import './ChatInterface.css'; // Make sure to create this CSS file

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSendClick = () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, fromUser: true }]);
      setInput('');
    }
  };

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSendClick();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="clear-chat-btn">Clear chat</button>
      </div>
      <div className="chat-body">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message ${message.fromUser ? 'user' : ''}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="chat-footer">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
        />
        <button onClick={handleSendClick} className="send-btn">Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
