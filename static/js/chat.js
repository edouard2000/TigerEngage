// Message Input //
const input = document.querySelector('.message-text')
const textarea = document.querySelector('.message-input-area')


input.addEventListener('input', function () {
   let line = input.value.split('\n').length
    console.log()
})


// Messages //
const messages = document.querySelector('.messagesContainer')

textarea.addEventListener('sendMsg', function(e) {
    e.preventDefault()

    writeMessage()
})

function addZero(num) {
    return num < 10 ? '0'+num : num
}

function writeMessage() {
    const time = new Date()
    let message = '<div class="sent-message"><span class="chatbox-message-item-text flex justify-start">${input.value.trim().replace(/\n/g, "<br>\n")}</span><span chass="chatbox-message-item-time">${addZero(time.getHours())}:${addZero(time.getMinutes())}</span></div>'

    messages.insertAdjacentHTML('beforeend', message)
    input.rows = 1
    input.focus()
    input.value = ''
}
//---------------------------------------------------------------//

$(document).ready(function() {
    const socket = io()

    socket.on('connect', function() {
      socket.send("User connected!");
    });

    socket.on('message', function(data) {
      $('#messages').append($('<p>').text(data));
    });

    $('#sendBtn').on('click', function() {
      socket.send($('message').val());
      $('message').val('');
    });
});


const socket = io();

        let messageContainer = document.querySelector(".messages")

        socket.on('connect', function() {
          socket.send("User connected!");
        })

        let messageInput = document.getElementById("messageInput")
        messageInput.addEventListener("keypress", (key) => {
          if (key.which === 13) {
            if (messageInput.value == "") return;
          
            socketio.emit("message", messageInput.value);
            messageInput.value = "";
          }
        })

        socket.on('message', (message_data) => {
          let messageElement = document.createElement("p")
          messageElement.innerText = message_data
          messageContainer.appendChild(messageElement)
        })




        socket.on('message', (data) => {
          createMessage(data.name, data.message)
          $('#this_user_msgs').append($('<p>').text(data));
        })

        const createMessage = (name, msg) => {
          const content = `
            <div class="text"> 
              <span>
                <strong>${name}</strong>: ${msg}
              </span>
              <span class="muted">
                ${timestamp}
              </span>
            </div>
          `;

          messages.innerHTML += content;
        }
        
        

          

        
        $('#Send').on('click', function() {
          socket.send($('message').val());
          $('message').val('');
        });

    {% for msg in messages %}
    <script type="text/javascript">
      createMessage("{{msg.name}}", "{{msg.message}}");
    </script>
    {% endfor %}