import React, { useState } from 'react';
import axios from 'axios';

const Chatbot = () => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    setMessage(e.target.value);
  };

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    // Add user message to the chat history
    setChatHistory([...chatHistory, { sender: 'user', message }]);
    setIsLoading(true);
    try {
      // Send message to the backend (FastAPI) endpoint
      const response = await axios.post('http://localhost:8000/chat', {
        message
      });

      // Add bot response to the chat history
      setChatHistory([
        ...chatHistory,
        { sender: 'bot', message: response.data.response }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setMessage('');
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot">
      <div className="chat-history">
        {chatHistory.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender}`}
          >
            {msg.sender === 'user' ? 'You: ' : 'Bot: '}
            {msg.message}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={message}
        onChange={handleInputChange}
        placeholder="Type a message"
      />
      <button onClick={handleSendMessage} disabled={isLoading}>
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
};

export default Chatbot;