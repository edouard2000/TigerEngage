let globalClassId = null;

document.addEventListener("DOMContentLoaded", function () {
  globalClassId = getClassIdFromUrl();

  document
    .getElementById("addQuestion")
    .addEventListener("click", () => fetchContent("/add-question"));

  document.getElementById("classUsers").addEventListener("click", function () {
    const classId = this.getAttribute("data-class-id");
    fetchContent(`/class/${classId}/userlist`);
  });

  const userListButton = document.getElementById("classUsers");
  if (userListButton) {
    userListButton.click();
  }

  document.getElementById("feedback").addEventListener("click", function () {
    const classId = this.getAttribute("data-class-id");
    fetchContent(`/class/${classId}/feedback`);
  });

  document
    .getElementById("liveChat")
    .addEventListener("click", () => fetchContent("/chat"));
  initializeStartEndToggle();

  document
    .querySelector(".edit-question-modal .close-button")
    .addEventListener("click", function () {
      document.getElementById("editQuestionModal").style.display = "none";
    });

  initializeQuestionEventListeners();
});



function showEditQuestionModal(
  questionId,
  currentQuestionText,
  currentAnswerText
) {
  document.getElementById("editQuestionModal").style.display = "block";
  document.getElementById("editQuestionText").value = currentQuestionText;
  document.getElementById("editAnswerText").value = currentAnswerText;
  document.getElementById("editingQuestionId").value = questionId;
}



function fetchContent(endpoint) {
  fetch(endpoint)
    .then((response) => response.text())
    .then((html) => {
      const dashboardContent = document.getElementById("dashboardContent");
      dashboardContent.innerHTML = html;

      if (endpoint.includes("/questions")) {
        initializeQuestionFormEventListeners();
        fetchQuestionsAndDisplay(globalClassId);
      } else if (endpoint === "/add-question") {
        initializeQuestionFormEventListeners();
      } else if (endpoint === "/chat") {
        initializeChat(); 
      }
    })
    .catch((error) => console.error("Error loading content:", error));
}



function initializeStartEndToggle() {
  const startClassBtn = document.getElementById("startClass");
  const classId = getClassIdFromUrl();
  checkSessionStatusAndUpdateButton(classId, startClassBtn);

  startClassBtn.addEventListener("click", function () {
    const action = this.textContent.includes("Start") ? "start" : "end";
    toggleClassSession(classId, action, startClassBtn);
  });
}

function toggleMoreInfo() {
  var infoContent = document.getElementById('moreInfoContent');
  var learnMoreBtn = document.getElementById('learnMoreBtn'); 

  if (infoContent.style.display === 'none' || !infoContent.style.display) {
      infoContent.style.display = 'block';
      learnMoreBtn.textContent = 'Close'; 
  } else {
      infoContent.style.display = 'none';
      learnMoreBtn.textContent = 'Learn More'; 
  }
}


function toggleClassSession(classId, action, button) {
  const endpoint = `/class/${classId}/${action}_session`;
  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": document
        .querySelector('meta[name="csrf-token"]')
        .getAttribute("content"),
    },
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        Swal.fire({
          icon: "success",
          title: "Success!",
          text: `Class session ${action === "start" ? "started" : "ended"} successfully.`,
          confirmButtonText: "OK",
        }).then((result) => {
          if (result.isConfirmed) {
            checkSessionStatusAndUpdateButton(classId, button);
          }
        });
      } else {
 
        Swal.fire({
          icon: "error",
          title: "Failed!",
          text: data.message, 
          confirmButtonText: "OK",
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: `An error occurred while trying to ${action} the class session: ${error.message}`,
        confirmButtonText: "OK",
      });
    });
}




function checkSessionStatusAndUpdateButton(classId, button) {
  fetch(`/class/${classId}/session_status`)
    .then((response) => response.json())
    .then((data) => {
      if (data.isActive) {
        button.textContent = "End Class";
        button.classList.add("bg-red-600");
        button.classList.remove("bg-green-800");
      } else {
        button.textContent = "Start Class";
        button.classList.add("bg-green-800");
        button.classList.remove("bg-red-600");
      }
    })
    .catch((error) => {
      console.error("Error checking session status:", error);
    });
}


function initializeQuestionFormEventListeners() {
  let csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
  const classId = globalClassId;

  const createQuestionBtn = document.getElementById("createQuestionBtn");
  const questionForm = document.getElementById("questionForm");

  if (createQuestionBtn && questionForm) {
    createQuestionBtn.addEventListener("click", function () {
      questionForm.classList.toggle("hidden");
      createQuestionBtn.classList.toggle("hidden");
    });
  }





  const addQuestionBtn = document.getElementById("addQuestionBtn");

  if (addQuestionBtn) {
    addQuestionBtn.addEventListener("click", function () {
      const questionInput = document.getElementById("questionInput");
      const answerInput = document.getElementById("answerInput");

      if (!questionInput.value.trim() || !answerInput.value.trim()) {
        Swal.fire({
          icon: "warning",
          title: "Incomplete Fields",
          text: "Please fill in both the question and the answer.",
          confirmButtonColor: "#0284c7",
          confirmButtonText: "OK",
        });
        return;
      }

      fetch(`/class/${classId}/add-question`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
          question_text: questionInput.value,
          correct_answer: answerInput.value,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              "Network response was not ok. Status: " + response.status
            );
          }
          return response.json();
        })
        .then((data) => {
          if (data.success) {
            questionInput.value = "";
            answerInput.value = "";
            fetchQuestionsAndDisplay(classId);
            questionForm.classList.add("hidden");
            createQuestionBtn.classList.remove("hidden");
            Swal.fire({
              icon: "success",
              title: "Question Added",
              text: "The question has been successfully added.",
              confirmButtonColor: "#0284c7", 
              confirmButtonText: "OK",
            });
          } else {
            Swal.fire({
              icon: "error",
              title: "Failed",
              text: "Failed to add the question. Please try again.",
              confirmButtonColor: "#0284c7",
              confirmButtonText: "OK",
            });
          }
        })
        .catch((error) => {
          console.error("Error adding question:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "An error occurred while trying to add the question.",
            confirmButtonColor: "#0284c7",
            confirmButtonText: "OK",
          });
          questionForm.classList.add("hidden");
          createQuestionBtn.classList.remove("hidden");
        });
    });
  }

  fetchQuestionsAndDisplay(classId);
}
function fetchQuestionsAndDisplay(classId) {
  console.log("Fetching questions...");
  fetch(`/class/${classId}/questions`)
    .then(response => response.json())
    .then(data => {
      const questionsContainer = document.getElementById("questionsList");
      if (!questionsContainer) {
        console.error("The questionsList container was not found on the page.");
        return;
      }
      questionsContainer.innerHTML = "";
      if (data.questions && data.questions.length > 0) {
        data.questions.forEach(question => {
          const questionElement = createQuestionElement(question);  
          questionsContainer.appendChild(questionElement); 
        });


        data.questions.forEach(question => {
          fetch(`/class/${classId}/question/${question.question_id}/status`)
            .then(statusResponse => statusResponse.json())
            .then(statusData => {
              if (statusData.success) {
                const questionElement = document.querySelector(`[data-question-id="${question.question_id}"]`);
                updateQuestionStatus(questionElement, statusData.isActive, statusData.isDisplayed);

                localStorage.setItem(`askState-${question.question_id}`, statusData.isActive.toString());
                localStorage.setItem(`displayState-${question.question_id}`, statusData.isDisplayed.toString());
              }
            })
            .catch(statusError => {
              console.error(`Error fetching status for question ${question.question_id}:`, statusError);
            });
        });

        initializeQuestionEventListeners();
      } else {
        questionsContainer.innerHTML = "<p>No questions found for this class.</p>";
      }
    })
    .catch(error => {8
      console.error("Error fetching questions:", error);
    });
}

function updateQuestionStatus(questionElement, isActive, isDisplayed) {
  if (questionElement) {
    questionElement.classList.toggle('active', isActive);
    questionElement.classList.toggle('displayed', isDisplayed);
  }
}



function createQuestionElement(question) {
  const isActive = localStorage.getItem(`askState-${question.question_id}`) === 'true';
  const isDisplayed = localStorage.getItem(`displayState-${question.question_id}`) === 'true';
  
  const element = document.createElement("div");
  element.className = "question-element flex justify-between items-center p-4 border border-gray-300 rounded-md mb-2 bg-sky-600 text-white";
  element.innerHTML = `
    <div class="flex-1">
        <div><span class="font-semibold">Q:</span> ${question.text}</div>
        <div><span class="font-semibold">A:</span> ${question.correct_answer}</div>
    </div>
    <div class="actions">
        <button class="edit-button py-1 px-3 rounded bg-yellow-500 hover:bg-yellow-600 transition duration-300" data-question-id="${question.question_id}">
            Edit
        </button>
        <button class="delete-button py-1 px-3 rounded bg-red-500 hover:bg-red-600 transition duration-300 ml-2" data-question-id="${question.question_id}">
            Delete
        </button>
        <button class="ask-button py-1 px-3 rounded ${isActive ? "bg-red-600" : "bg-green-500"} hover:bg-green-600 transition duration-300 ml-2" data-question-id="${question.question_id}" data-is-active="${isActive}">
            ${isActive ? "Stop" : "Ask"}
        </button>
        <button class="display-button py-1 px-3 rounded ${isDisplayed ? "bg-blue-700" : "bg-blue-500"} hover:bg-blue-700 transition duration-300 ml-2" data-question-id="${question.question_id}" data-is-displayed="${isDisplayed}">
            ${isDisplayed ? "UnDisplay" : "Display"}
        </button>
    </div>
  `;

  element.querySelector(".ask-button").addEventListener("click", function () {
    handleAskStopQuestion(question.question_id, this);
  });
  element.querySelector(".display-button").addEventListener("click", function () {
    toggleDisplay(question.question_id, this);
  });
  element.querySelector(".delete-button").addEventListener("click", function () {
    deleteQuestion(question.question_id);
  });
  element.querySelector(".edit-button").addEventListener("click", function () {
    showEditQuestionModal(question.question_id, question.text, question.correct_answer);
  });

  return element;
}



function toggleDisplay(questionId, button) {
  const isDisplayed = button.getAttribute('data-is-displayed') === 'true';
  const endpoint = `/class/${globalClassId}/question/${questionId}/toggle_display`;
  fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
    },
    body: JSON.stringify({ displayed: !isDisplayed })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      button.setAttribute('data-is-displayed', (!isDisplayed).toString());
      button.textContent = isDisplayed ? 'Display' : 'UnDisplay';
      Swal.fire({
        icon: 'success',
        title: 'Success',
        text: `Question has been ${!isDisplayed ? 'displayed' : 'undisplayed'} successfully.`
      });
    } else {
      // Handle specific server-side error messages
      Swal.fire({
        icon: 'error',
        title: 'Action Denied',
        text: data.message,
        confirmButtonColor: '#d33',
        confirmButtonText: 'OK'
      });
    }
  })
  .catch(error => {
    console.error('Error toggling display:', error);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: `An error occurred: ${error.message}`
    });
  });
}



function handleAskStopQuestion(questionId, buttonElement) {
  const currentState = buttonElement.getAttribute("data-is-active") === "true";
  const isAsking = !currentState;
  const endpoint = `/class/${globalClassId}/question/${questionId}/ask`;
  const actionText = isAsking ? "ask" : "stop";

  Swal.fire({
    title: `Are you sure you want to ${actionText} this question?`,
    text: `This will ${isAsking ? "start" : "stop"} showing the question to the class.`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: `Yes, ${actionText} it!`,
  }).then((result) => {
    if (result.isConfirmed) {
      fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
        },
        body: JSON.stringify({ active: isAsking }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            buttonElement.setAttribute("data-is-active", isAsking.toString());
            updateAskButtons(questionId, isAsking);
            Swal.fire({
              icon: "success",
              title: "Success!",
              text: `Question was successfully ${isAsking ? "asked" : "stopped"}.`,
              confirmButtonColor: "#3085d6",
              confirmButtonText: "OK",
            });
          } else {
            Swal.fire({
              icon: "error",
              title: "Activation Conflict",
              text: data.message,
              confirmButtonColor: "#d33",
              confirmButtonText: "OK",
            });
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          Swal.fire({
            icon: "error",
            title: "Error",
            text: `An error occurred while trying to ${actionText} the question: ${error.message}`,
            confirmButtonColor: "#d33",
            confirmButtonText: "Close",
          });
        });
    }
  });
}


function updateAskButtons(questionId, isAsking) {
  const buttons = document.querySelectorAll(".ask-button");
  buttons.forEach((btn) => {
    if (btn.getAttribute("data-question-id") === questionId) {
      btn.textContent = isAsking ? "Stop" : "Ask";
      btn.setAttribute("data-is-active", isAsking.toString());
    }
    btn.disabled =
      isAsking && btn.getAttribute("data-question-id") !== questionId;
  });
}



function initializeQuestionEventListeners() {
  const askButtons = document.querySelectorAll(".ask-button");
  askButtons.forEach((button) => {
    if (!button.dataset.listenerAdded) {
      button.addEventListener("click", function () {
        const isActive = button.getAttribute("data-is-active") === "true";
        const newIsActive = !isActive;

        handleAskStopQuestion(this.dataset.questionId, this);
        button.setAttribute("data-is-active", newIsActive.toString());
      });
      button.dataset.listenerAdded = "true";
    }
  });
}

function getClassIdFromUrl() {
  const urlParts = window.location.pathname.split("/");
  return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
}



function deleteQuestion(questionId) {
  Swal.fire({
    title: "Are you sure?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Yes, delete it!"
  }).then((result) => {
    if (result.isConfirmed) {
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
      fetch(`/class/${globalClassId}/question/${questionId}/delete`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrfToken
        },
        credentials: "include"
      })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          Swal.fire("Deleted!", "Your question has been deleted.", "success");
          fetchQuestionsAndDisplay(globalClassId);
        } else {
          throw new Error(data.message);
        }
      })
      .catch((error) => {
        console.error("Error deleting question:", error);
        Swal.fire({
          icon: "error",
          title: "Error",
          text: `An error occurred: ${error.message}`,
          confirmButtonColor: "#d33",
          confirmButtonText: "OK"
        });
      });
    }
  });
}


document
  .getElementById("editQuestionForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    const questionId = document.getElementById("editingQuestionId").value;
    const questionText = document.getElementById("editQuestionText").value;
    const answerText = document.getElementById("editAnswerText").value;

    fetch(`/class/${globalClassId}/question/${questionId}/edit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
      },
      credentials: "include",
      body: JSON.stringify({
        question_text: questionText,
        correct_answer: answerText,
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        fetchQuestionsAndDisplay(globalClassId);
        document.getElementById("editQuestionModal").style.display = "none";
        Swal.fire({
          title: 'Success!',
          text: 'Question updated successfully.',
          icon: 'success',
          confirmButtonText: 'Ok'
        });
      } else {
        throw new Error(data.message);
      }
    })
    .catch(error => {
      console.error("Error updating question:", error);
      Swal.fire({
        title: 'Error!',
        text: error.message,
        icon: 'error',
        confirmButtonText: 'Ok'
      });
    });
  });




function fetchEditModalContent(
  questionId,
  currentQuestionText,
  currentAnswerText
) {
  fetch("/edit-question")
    .then((response) => response.text())
    .then((html) => {
      const modalContainer = document.getElementById("modalContainer");
      if (!modalContainer) {
        console.error("Modal container not found in the DOM");
        return;
      }
      modalContainer.innerHTML = html;

      document.getElementById("editQuestionText").value = currentQuestionText;
      document.getElementById("editAnswerText").value = currentAnswerText;
      document.getElementById("editingQuestionId").value = questionId;

      const editModal = document.getElementById("editQuestionModal");
      if (editModal) {
        editModal.style.display = "block";
      } else {
        console.error("Edit modal not found in the loaded content");
      }

      const closeButton = modalContainer.querySelector(".close-button");
      if (closeButton) {
        closeButton.addEventListener("click", function () {
          editModal.style.display = "none";
        });
      } else {
        console.error("Close button not found in the loaded content");
      }
    })
    .catch((error) => {
      console.error("Error fetching the edit question modal:", error);
    });
}





function showEditQuestionModal(
  questionId,
  currentQuestionText,
  currentAnswerText
) {
  document.getElementById("editQuestionModal").style.display = "block";
  document.getElementById("editQuestionText").value = currentQuestionText;
  document.getElementById("editAnswerText").value = currentAnswerText;
  document.getElementById("editingQuestionId").value = questionId;
}

document
  .getElementById("editQuestionForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    submitEditForm();
  });



function submitEditForm() {
  const questionId = document.getElementById("editingQuestionId").value;
  const questionText = document.getElementById("editQuestionText").value;
  const answerText = document.getElementById("editAnswerText").value;

  fetch(`/class/${globalClassId}/question/${questionId}/edit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": document
        .querySelector('meta[name="csrf-token"]')
        .getAttribute("content"),
    },
    body: JSON.stringify({
      question_text: questionText,
      correct_answer: answerText,
    }),
  })
    .then((response) => {
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        Swal.fire({
          icon: "success",
          title: "Success",
          text: "Question successfully updated.",
          confirmButtonColor: "#3085d6",
          confirmButtonText: "OK",
        });
        fetchQuestionsAndDisplay(globalClassId);
        document.getElementById("editQuestionModal").style.display = "none";
      } else {
        throw new Error("Failed to update the question.");
      }
    })
    .catch((error) => {
      console.error("Error updating question:", error);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: `An error occurred: ${error.message}`,
        confirmButtonColor: "#d33",
        confirmButtonText: "OK",
      });
    });
}




document.getElementById("logoutButton").addEventListener("click", function (e) {
  e.preventDefault(); 
  logout();  
});

function logout() {
  Swal.fire({
      title: 'Are you sure you want to logout?',
      text: "Make sure all activities are properly closed.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, logout!'
  }).then((result) => {
      if (result.isConfirmed) {
          fetch("/logout", {
              method: "GET",
              headers: {
                  "Content-Type": "application/json",
              },
              credentials: "include"
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  Swal.fire(
                      'Logged Out!',
                      'You have been successfully logged out.',
                      'success'
                  ).then(() => {
                      window.location.href = '/'; 
                  });
              } else {
                  Swal.fire({
                      icon: 'error',
                      title: 'Logout Failed',
                      text: data.message,
                      confirmButtonText: 'OK'
                  });
              }
          })
          .catch(error => {
              console.error('Logout error:', error);
              Swal.fire({
                  icon: 'error',
                  title: 'Error',
                  text: 'An unexpected error occurred during logout.',
                  confirmButtonText: 'OK'
              });
          });
      }
  });
}



function initializeChat() {
  var messageInput = document.getElementById('message');
  var messagesContainer = document.querySelector('.chat-messages');
  if (!messageInput || !messagesContainer) {
    console.error('Chat initialization failed: Essential elements are missing.');
    return;
  }

  const classId = getClassIdFromUrl();
  fetchMessages(classId);

  var socket = io.connect(window.location.origin);
  function sendMessage() {
    var content = messageInput.value.trim();
    if (content) {
      console.log('Sending message:', content);  
      socket.emit('send_message', { content: content });
      messageInput.value = ''; 
    }
  }

  var sendButton = document.querySelector('[aria-label="Send Message"]');
  if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
  } else {
    console.error('Send button not found.');
  }

  messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      sendMessage();
      e.preventDefault();
    }
  });

  socket.on('receive_message', function(data) {
    console.log('Received message:', data); 
    var messageElement = document.createElement('div');
    messageElement.textContent = data.content;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;  
});

  socket.on('connect_error', function(err) {
    console.error('Connection to the server lost:', err);
  });

  socket.on('connect', function() {
    console.log('Connected to WebSocket server.');
  });
}



function fetchMessages(classId) {
  fetch(`/chat/${classId}/messages`)
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              data.messages.forEach(message => {
                  displayMessage(message);
              });
          } else {
              console.error('Failed to load messages:', data.error);
          }
      })
      .catch(error => console.error('Error fetching chat messages:', error));
}

function displayMessage(message) {
  const messagesContainer = document.querySelector('.chat-messages');
  const messageElement = document.createElement('div');
  messageElement.className = 'chat-message p-3 rounded-lg shadow mb-3 flex justify-between items-center'; 
  messageElement.innerHTML = `
    <p class="flex-1">${message.text}</p>
    <div class="chat-buttons">
      <button class="chat-button bg-blue-500 hover:bg-blue-700 text-white rounded py-1 px-3" onclick="editMessage('${message.message_id}')">Edit</button>
      <button class="chat-button bg-red-500 hover:bg-red-700 text-white rounded py-1 px-3" onclick="deleteMessage('${message.message_id}')">Delete</button>
      <button class="chat-button bg-green-500 hover:bg-green-700 text-white rounded py-1 px-3" onclick="replyToMessage('${message.message_id}')">Reply</button>
    </div>
  `;
  messagesContainer.appendChild(messageElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}



function editMessage(messageId) {
  console.log('Editing message:', messageId);
  // Add your editing logic here
}

function deleteMessage(messageId) {
  console.log('Deleting message:', messageId);
  // Add your deletion logic here
}

function replyToMessage(messageId) {
  console.log('Replying to message:', messageId);
  // Add your reply logic here
}
