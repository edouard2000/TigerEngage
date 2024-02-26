import { useState } from 'react';

const dummyMessages = [
  {
    id: 1,
    text: 'What is the main concept of Object-Oriented Programming?',
    sender: 'user',
  },
  {
    id: 2,
    text: "It's a programming paradigm based on the concept of objects, which can contain data and code: data in the form of fields, and code, in the form of procedures.",
    sender: 'responder',
  },
  { id: 3, text: 'How can I improve my algorithm skills?', sender: 'user' },
];

const ChatSystem = () => {
  const [messages, setMessages] = useState(dummyMessages);
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const nextId = messages.length + 1;
    setMessages([
      ...messages,
      { id: nextId, text: newMessage, sender: 'user' },
    ]);
    setNewMessage('');
  };

  return (
    <div className="mx-auto my-8 max-w-md rounded-lg bg-white p-4 shadow">
      <h2 className="mb-4 text-lg font-semibold">Classroom Chat</h2>
      <div className="mb-4 h-64 overflow-y-auto">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`my-2 rounded p-2 ${message.sender === 'user' ? 'ml-auto bg-blue-200' : 'mr-auto bg-gray-200'}`}
            style={{ maxWidth: '80%' }}
          >
            <p className="text-sm">{message.text}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleSendMessage} className="flex">
        <input
          type="text"
          className="mr-2 flex-1 rounded border border-gray-300 p-2"
          placeholder="Type your message here..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <button
          type="submit"
          className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatSystem;
