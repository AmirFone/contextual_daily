import React, { useState } from 'react';
import './ChatInterface.css'; // Ensure this CSS file is properly linked for styling

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const sendQueryToServer = async (userInput) => {
    let uniqueUserId = localStorage.getItem("uniqueUserId");
    if (!uniqueUserId) {
      console.error("Error: Unique user ID not found in local storage.");
    }
    setIsSending(true);
    try {
      const response = await fetch("https://contextual-9b9c45ec5823.herokuapp.com/chat/query", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userInput,
          context: messages.map(msg => msg.text).join("\n"),
          unique_user_id: uniqueUserId,
        }),
      });

      if (response.ok) {
        const { response: serverResponse } = await response.json();
  
        // Format the server response here
        const formattedResponse = serverResponse
          .replace(/\\n/g, '\n') // Convert escaped new lines back to actual new lines
          .replace(/(^"|"$)/g, ''); // Remove quotation marks at the start or end of the response
  
        setMessages(messages => [...messages, { text: userInput, fromUser: true }, { text: formattedResponse, fromUser: false }]);
      } else {
        console.error('Error from server');
      }
    } catch (error) {
      console.error('Error sending query to server', error);
    }
    setIsSending(false);
  };

  const handleSendClick = () => {
    if (input.trim()) {
      sendQueryToServer(input.trim());
      setInput('');
    }
  };

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };


  const clearMessages = () => {
    setMessages([]);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSendClick();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button onClick={clearMessages} className="clear-chat-btn">Clear chat</button>
      </div>
      <div className="chat-body">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message ${message.fromUser ? 'user' : 'server'}`}>
            {message.text}
          </div>
        ))}
        {isSending && <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>}
      </div>
      <div className="chat-footer">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message here..."
        />
        <button onClick={handleSendClick} className="send-btn">Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
