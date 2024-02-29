import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';

const dummyMessages = [
  {
    id: 1,
    text: 'What is the main concept of Object-Oriented Programming?',
    sender: 'user',
    replies: [],
    timestamp: new Date(Date.now() - 1500),
  },
  {
    id: 2,
    text: "It's a programming paradigm based on the concept of objects, which can contain data and code: data in the form of fields, and code, in the form of procedures.",
    sender: 'responder',
    replies: [],
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
  },
  {
    id: 3,
    text: 'How can I improve my algorithm skills?',
    sender: 'user',
    replies: [],
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
  },
];

const ChatSystem = () => {
  const inputRef = React.createRef();

  const [messages, setMessages] = useState(dummyMessages);
  const [newMessage, setNewMessage] = useState('');
  const [replyToId, setReplyToId] = useState(null);
  const [editingMessage, setEditingMessage] = useState(null);

  const handleReply = (id) => {
    setReplyToId(id);
    setEditingMessage(null);
    inputRef.current?.focus();
  };

  const handleDeleteMessage = (id, isReply = false) => {
    if (isReply) {
      setMessages(
        messages.map((message) => ({
          ...message,
          replies: message.replies.filter((reply) => reply.id !== id),
        })),
      );
    } else {
      setMessages(messages.filter((message) => message.id !== id));
    }
  };

  const handleEditMessage = (message, isReply = false) => {
    setEditingMessage({ ...message, isReply });
    setNewMessage(message.text);
    if (isReply) {
      setReplyToId(message.id);
    }
  };

  const formatTimestamp = (timestamp) => {
    return formatDistanceToNow(timestamp, {
      addSuffix: true,
      includeSeconds: true,
    });
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage) return;

    if (editingMessage) {
      const updatedMessages = messages.map((message) => {
        if (message.id === editingMessage.id) {
          return { ...message, text: trimmedMessage };
        } else if (message.replies) {
          const updatedReplies = message.replies.map((reply) => {
            if (reply.id === editingMessage.id) {
              return { ...reply, text: trimmedMessage };
            }
            return reply;
          });
          return { ...message, replies: updatedReplies };
        }
        return message;
      });
      setMessages(updatedMessages);
    } else {
      const nextId = messages.length + 1;
      const newMessageObject = {
        id: nextId,
        text: trimmedMessage,
        sender: 'user',
        replies: [],
        timestamp: new Date(),
      };
      if (replyToId) {
        const messageIndex = messages.findIndex((m) => m.id === replyToId);
        if (messageIndex !== -1) {
          messages[messageIndex].replies.push(newMessageObject);
        }
      } else {
        setMessages([...messages, newMessageObject]);
      }
    }
    setNewMessage('');
    setReplyToId(null);
    setEditingMessage(null);
  };

  return (
    <div className="fixed inset-0 flex flex-col bg-gray-800">
      <h2 className="p-4 text-center text-lg font-bold text-white">
        Class Chat
      </h2>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <div key={message.id} className="mb-4">
            <div
              className={`rounded p-2 shadow ${
                message.sender === 'user'
                  ? 'ml-auto bg-blue-500 text-white'
                  : 'mr-auto bg-gray-100 text-black'
              }`}
              style={{ maxWidth: '75%' }}
            >
              <p>{message.text}</p>
              <span className="text-xs text-gray-500">
                {formatTimestamp(message.timestamp)}
              </span>
              <div className="flex justify-end">
                <button
                  onClick={() => handleReply(message.id)}
                  className="text-xs text-gray-400 hover:underline"
                >
                  Reply
                </button>
                <button
                  onClick={() => handleEditMessage(message)}
                  className="mx-2 text-xs text-gray-400 hover:underline"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteMessage(message.id)}
                  className="text-xs text-red-500 hover:underline"
                >
                  Delete
                </button>
              </div>
            </div>
            {message.replies.map((reply) => (
              <div
                key={reply.id}
                className="ml-4 mt-2 border-l-2 border-gray-500 pl-4"
              >
                <p className="rounded bg-gray-200 p-2 text-sm">{reply.text}</p>
                <span className="text-xs text-gray-500">
                  {formatTimestamp(reply.timestamp)}
                </span>

                <div className="flex justify-end">
                  <button
                    onClick={() => handleReply(message.id)}
                    className="text-xs text-gray-400 hover:underline"
                  >
                    Reply
                  </button>
                  <button
                    onClick={() => handleEditMessage(reply, true)}
                    className="mx-2 text-xs text-gray-400 hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteMessage(reply.id, true)}
                    className="text-xs text-red-500 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="bg-black p-4">
        {replyToId && (
          <p className="mb-2 text-sm text-gray-300">
            Replying to message #{replyToId}
          </p>
        )}
        {editingMessage && (
          <p className="mb-2 text-sm text-gray-300">
            Editing message #{editingMessage.id}
          </p>
        )}
        <form onSubmit={handleSendMessage} className="flex">
          <input
            type="text"
            className="flex-1 rounded p-2 text-black"
            placeholder="Type your message here..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <button
            type="submit"
            className="ml-2 rounded bg-blue-500 px-4 py-2 font-bold text-white hover:bg-blue-700"
          >
            {editingMessage ? 'Update' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatSystem;
