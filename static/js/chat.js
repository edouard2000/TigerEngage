// file: chat.js 
// author: Edouard KWIZERA


function fetchCurrentUserId() {
  fetch('/get-current-user')
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              localStorage.setItem('userId', data.userId);
              currentUserId = data.userId;
              initializeChat();
          } else {
              console.error('Failed to get current user ID:', data.message);
              Swal.fire("Error", "Failed to load user data. Please log in again.", "error");
          }
      })
      .catch(error => {
          console.error('Error fetching current user ID:', error);
          Swal.fire("Error", "Failed to fetch user data.", "error");
      });
}

document.addEventListener("DOMContentLoaded", fetchCurrentUserId);


var socket;
var currentUserId = localStorage.getItem("userId");
console.log("Current user ID:", currentUserId);

function initializeChat() {
  console.log("Current user ID:", currentUserId);
  if (!currentUserId) {
    console.error("Current user ID not set. Unable to initialize chat.");
    return;
}
  var messageInput = document.getElementById("message");
  var messagesContainer = document.querySelector(".chat-messages");

  if (!messageInput || !messagesContainer) {
    Swal.fire(
      "Error",
      "Chat initialization failed: Essential elements are missing.",
      "error"
    );
    return;
  }

  socket = io.connect(window.location.origin);

  document
    .querySelector('[aria-label="Send Message"]')
    .addEventListener("click", () => {
      let messageText = messageInput.value.trim();
      if (messageText) {
        sendMessage(messageText);
        messageInput.value = "";
      } else {
        Swal.fire("Notice", "Please enter a message before sending.", "info");
      }
    });

  messageInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && messageInput.value.trim()) {
      sendMessage(messageInput.value.trim());
      messageInput.value = "";
      e.preventDefault();
    }
  });

  fetchAndDisplayMessages(getClassIdFromUrl());

  socket.on('new_message', function(message) {
    console.log('New message received:', message);
    console.log('Is this message from the current user?', message.sender_id === currentUserId);
    const isSender = message.sender_id === currentUserId;
    if (!document.getElementById(`msg-${message.message_id}`)) {
      displayMessage(message, isSender);
    }
  });

  socket.on("error", function (data) {
    console.error("Socket error received:", data);
    Swal.fire("Error", data.error || "An unknown error occurred.", "error");
  });
}


function sendMessage(content) {
  console.log("Attempting to send message:", content);
  if (isClassActive) {
      socket.emit('send_message', { content: content, sender_id: currentUserId });
  } else {
      console.log("Failed to send message: Class is not active");
      Swal.fire('Error', 'Cannot send message. The class has not started.', 'error');
  }
}


function fetchAndDisplayMessages(classId) {
  console.log("Fetching messages for class ID:", classId);
  clearChatMessages();
  fetch(`/chat/${classId}/messages`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.isClassActive) {
        isClassActive = data.isClassActive;
        const currentUserIdFromServer = data.currentUserId;
        sender_id = currentUserIdFromServer;
        data.messages.forEach((message) => {
          const isSender = message.sender_id === currentUserIdFromServer;
          displayMessage(message, isSender);
        });
      } else {
        isClassActive = false;
        const errorMessage = data.isClassActive
          ? "Failed to load messages."
          : "The class has not started yet.";
        console.error("Chat Error:", errorMessage, data.error || "");
        Swal.fire("Chat Unavailable", errorMessage, "error");
      }
    })
    .catch((error) => {
      console.error("Error fetching chat messages:", error);
      Swal.fire("Error", "Failed to fetch messages from the server.", "error");
    });
}

function displayMessage(message, isSender) {
  const messagesContainer = document.querySelector(".chat-messages");
  if (message.text.trim() === "") return;

  const textClass = isSender ? "text-white" : "text-gray-700";
  const bgClass = isSender ? "bg-blue-500" : "bg-gray-200";
  const alignClass = isSender ? "float-right" : "float-left";
  const messageElement = document.createElement("div");
  messageElement.id = `msg-${message.message_id}`;
  messageElement.className = `rounded-xl px-4 py-2 mb-2 ${bgClass} ${textClass} ${alignClass}`;


  const roleLabel = document.createElement("div");
  roleLabel.className = isSender ? "role-label-sender" : "role-label-receiver";
  roleLabel.textContent = message.role;
  messageElement.appendChild(roleLabel);

  const messageText = document.createElement("div");
  messageText.textContent = message.text;
  messageElement.appendChild(messageText);

  messagesContainer.appendChild(messageElement);


  const clearFix = document.createElement("div");
  clearFix.className = "clear-both";
  messagesContainer.appendChild(clearFix);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function clearChatMessages() {
  const messagesContainer = document.querySelector(".chat-messages");
  messagesContainer.innerHTML = "";
}



