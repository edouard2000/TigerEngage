document.addEventListener('DOMContentLoaded', function() {
    var socket = io(); // Connect to the Socket.IO server

    // Elements
    var messageInput = document.getElementById('message-input');
    var sendButton = document.getElementById('send-button');
    var messagesDiv = document.getElementById('messages');

    // Emit a message to the server when the send button is clicked
    sendButton.onclick = function() {
        var text = messageInput.value.trim();
        if (text.length > 0) {
            socket.emit('message', { text: text });
            messageInput.value = '';
        }
    };

    // Listen for messages from the server
    socket.on('message', function(data) {
        var item = document.createElement('div');
        item.textContent = data.text;
        messagesDiv.appendChild(item);
        // Scroll to the bottom of the message display area
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
});
