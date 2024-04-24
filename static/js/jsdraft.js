// Main initializer function to set up the page once it's fully loaded
function initializePage() {
  const classId = getClassIdFromUrl();

  setupEventListeners(classId);
  initializeStartEndToggle(classId);
}

// Set up all required event listeners
function setupEventListeners(classId) {
  document.getElementById("addQuestion")
      .addEventListener("click", () => fetchContent("/add-question"));

  const classUsersButton = document.getElementById("classUsers");
  classUsersButton.addEventListener("click", () => fetchContent(`/class/${classId}/userlist`));

  // Automatically trigger the user list load if the button is present
  if (classUsersButton) {
      classUsersButton.click();
  }

  document.getElementById("feedback")
      .addEventListener("click", () => fetchContent(`/class/${classId}/feedback`));

  document.getElementById("liveChat")
      .addEventListener("click", () => fetchContent("/chat"));

  // Close button in the edit question modal
  document.querySelector(".edit-question-modal .close-button")
      .addEventListener("click", () => {
          document.getElementById("editQuestionModal").style.display = "none";
      });
}

// Initialize the toggle functionality for starting and ending class sessions
function initializeStartEndToggle(classId) {
  const startClassBtn = document.getElementById("startClass");
  checkSessionStatusAndUpdateButton(classId, startClassBtn);

  startClassBtn.addEventListener("click", function () {
      const action = this.textContent.includes("Start") ? "start" : "end";
      toggleClassSession(classId, action, startClassBtn);
  });
}

// Helper function to extract the class ID from the URL
function getClassIdFromUrl() {
  const urlParts = window.location.pathname.split("/");
  return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
}

// Event listener for DOMContentLoaded to ensure everything is set up once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", initializePage);


// Toggle the session status based on user action
function toggleClassSession(classId, action, button) {
  const endpoint = `/class/${classId}/${action}_session`;
  fetch(endpoint, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": getCsrfToken(),
      },
      credentials: "include",
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          displayAlert('success', 'Success!', `Class session ${action === "start" ? "started" : "ended"} successfully.`);
          checkSessionStatusAndUpdateButton(classId, button);
      } else {
          displayAlert('error', 'Failed!', data.message || `Failed to ${action} class session.`);
      }
  })
  .catch(error => {
      console.error("Error:", error);
      displayAlert('error', 'Oops...', `An error occurred while trying to ${action} the class session.`);
  });
}

// Check the current session status and update the button accordingly
function checkSessionStatusAndUpdateButton(classId, button) {
  fetch(`/class/${classId}/session_status`, {
      credentials: "include"
  })
  .then(response => response.json())
  .then(data => {
      button.textContent = data.isActive ? "End Class" : "Start Class";
      button.classList.toggle("bg-red-600", data.isActive);
      button.classList.toggle("bg-green-800", !data.isActive);
  })
  .catch(error => {
      console.error("Error checking session status:", error);
  });
}

// Utility to fetch CSRF token from the DOM
function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]').getAttribute("content");
}

// Utility to display alerts using SweetAlert2
function displayAlert(icon, title, text) {
  Swal.fire({
      icon: icon,
      title: title,
      text: text,
      confirmButtonText: 'OK'
  });
}


// Fetch content from the server and update the UI accordingly
function fetchContent(endpoint) {
  fetch(endpoint)
  .then(response => response.text())
  .then(html => {
      const dashboardContent = document.getElementById("dashboardContent");
      dashboardContent.innerHTML = html;

      // Check if endpoint involves questions to initialize specific listeners
      if (endpoint.includes("/questions")) {
          initializeQuestionFormEventListeners();
          fetchQuestionsAndDisplay(getClassIdFromUrl());
      } else if (endpoint === "/add-question") {
          initializeQuestionFormEventListeners();
      }
  })
  .catch(error => {
      console.error("Error loading content:", error);
  });
}

// Display the modal for editing a question with pre-filled data
function showEditQuestionModal(questionId, currentQuestionText, currentAnswerText) {
  const modal = document.getElementById("editQuestionModal");
  modal.style.display = "block";
  document.getElementById("editQuestionText").value = currentQuestionText;
  document.getElementById("editAnswerText").value = currentAnswerText;
  document.getElementById("editingQuestionId").value = questionId;
}




// Creates an HTML element for a question with associated actions
function createQuestionElement(question) {
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
          <button class="ask-button py-1 px-3 rounded ${question.is_active ? "bg-red-600" : "bg-green-500"} hover:bg-green-600 transition duration-300 ml-2" data-question-id="${question.question_id}" data-is-active="${question.is_active}">
              ${question.is_active ? "Stop" : "Ask"}
          </button>
          <button class="display-button py-1 px-3 rounded bg-blue-500 hover:bg-blue-700 transition duration-300 ml-2" data-question-id="${question.question_id}">
              Display
          </button>
      </div>
  `;
  addQuestionEventListeners(element, question);
  return element;
}

// Fetches questions from the server and updates the UI accordingly
function fetchQuestionsAndDisplay(classId) {
  fetch(`/class/${classId}/questions`)
  .then(response => response.json())
  .then(data => {
      const questionsContainer = document.getElementById("questionsList");
      questionsContainer.innerHTML = "";
      if (data.questions && data.questions.length > 0) {
          data.questions.forEach(question => {
              questionsContainer.appendChild(createQuestionElement(question));
          });
      } else {
          questionsContainer.innerHTML = "<p>No questions found for this class.</p>";
      }
  })
  .catch(error => {
      console.error("Error fetching questions:", error);
  });
}

// Adds event listeners to question elements for interactive actions
function addQuestionEventListeners(element, question) {
  element.querySelector(".edit-button").addEventListener("click", () => {
      showEditQuestionModal(question.question_id, question.text, question.correct_answer);
  });
  element.querySelector(".delete-button").addEventListener("click", () => {
      deleteQuestion(question.question_id);
  });
  element.querySelector(".ask-button").addEventListener("click", function() {
      const isActive = this.getAttribute("data-is-active") === "true";
      handleAskStopQuestion(question.question_id, !isActive, this);
  });
  element.querySelector(".display-button").addEventListener("click", () => {
      toggleDisplay(question.question_id);
  });
}


// Updates the state of buttons based on the activity status of questions
function updateButtonsStateBasedOnActivity() {
  const askButtons = document.querySelectorAll(".ask-button");
  let isActiveQuestionPresent = false;

  askButtons.forEach((button) => {
      const isActive = button.getAttribute("data-is-active") === "true";
      button.textContent = isActive ? "Stop" : "Ask";

      if (isActive) {
          isActiveQuestionPresent = true;
      }
  });

  if (isActiveQuestionPresent) {
      askButtons.forEach((button) => {
          const isActive = button.getAttribute("data-is-active") === "true";
          if (!isActive) {
              button.disabled = true;
          }
      });
  }
}

// Updates the visibility of a question based on the desired display state
function updateDisplayState(questionId, isDisplayed) {
  const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
  if (questionElement) {
      questionElement.style.display = isDisplayed ? 'block' : 'none';
  }
}


// Fetches and populates the content for the edit question modal
function fetchEditModalContent(questionId, currentQuestionText, currentAnswerText) {
  fetch("/edit-question")
  .then(response => response.text())
  .then(html => {
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
  .catch(error => {
      console.error("Error fetching the edit question modal:", error);
  });
}

// Displays the edit question modal and populates it with the question and answer
function showEditQuestionModal(questionId, currentQuestionText, currentAnswerText) {
  const modal = document.getElementById("editQuestionModal");
  modal.style.display = "block";
  document.getElementById("editQuestionText").value = currentQuestionText;
  document.getElementById("editAnswerText").value = currentAnswerText;
  document.getElementById("editingQuestionId").value = questionId;
}


// Retrieves the CSRF token from the document's meta tags
function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]').getAttribute("content");
}

// Displays a SweetAlert2 alert with the given parameters
function displayAlert(icon, title, text, confirmButtonText = 'OK') {
  Swal.fire({
      icon: icon,
      title: title,
      text: text,
      confirmButtonText: confirmButtonText
  });
}
