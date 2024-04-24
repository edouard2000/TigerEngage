let globalClassId = null;

document.addEventListener("DOMContentLoaded", function () {
  globalClassId = getClassIdFromUrl();
  
  document.getElementById("addQuestion")
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

  // document.getElementById("reviews").addEventListener("click", function () {
  //   const classId = this.getAttribute("data-class-id");
  //   fetchContent(`/class/${classId}/reviews`);
  // });
  
  document.getElementById("liveChat")
    .addEventListener("click", () => fetchContent("/chat"));
  initializeStartEndToggle();

  document.querySelector(".edit-question-modal .close-button")
    .addEventListener("click", function () {
      document.getElementById("editQuestionModal").style.display = "none";
    });
  
  // document.getElementById("openEditModal").addEventListener("click", function () {
  //   fetch("/edit_question_modal")
  //     .then((response) => response.text())
  //     .then((html) => {
  //       document.getElementById("modalContainer").innerHTML = html;
  //       document.getElementById("editQuestionModal").style.display = "block";
  //     })
  //     .catch((error) => {
  //       console.error("Error fetching the edit question modal:", error);
  //     });
  // });
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
          icon: 'success',
          title: 'Success!',
          text: `Class session ${action === "start" ? "started" : "ended"} successfully.`,
          confirmButtonText: 'OK'
        }).then((result) => {
          if (result.isConfirmed) {
            checkSessionStatusAndUpdateButton(classId, button);
          }
        });
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Failed!',
          text: data.message || `Failed to ${action} class session.`,
          confirmButtonText: 'OK'
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      Swal.fire({
        icon: 'error',
        title: 'Oops...',
        text: `An error occurred while trying to ${action} the class session.`,
        confirmButtonText: 'OK'
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
        alert("Please fill in both the question and the answer.");
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
          } else {
            alert("Failed to add the question. Please try again.");
          }
        })
        .catch((error) => {
          console.error("Error adding question:", error);
          alert("An error occurred while trying to add the question.");
          questionForm.classList.add("hidden");
          createQuestionBtn.classList.remove("hidden");
        });
    });
  }

  fetchQuestionsAndDisplay(classId);
}
function fetchQuestionsAndDisplay(classId) {
  fetch(`/class/${classId}/questions`)
    .then((response) => response.json())
    .then((data) => {
      const questionsContainer = document.getElementById("questionsList");
      if (!questionsContainer) {
        console.error("The questionsList container was not found on the page.");
        return; 
      }
      questionsContainer.innerHTML = "";
      if (data.questions && data.questions.length > 0) {
        data.questions.forEach((question) => {
          const questionElement = createQuestionElement(question);
          questionsContainer.appendChild(questionElement);
        });
        initializeQuestionEventListeners();
        updateButtonsStateBasedOnActivity();
      } else {
        questionsContainer.innerHTML = "<p>No questions found for this class.</p>";
      }
    })
    .catch((error) => {
      console.error("Error fetching questions:", error);
    })
    .finally(() => {
      setupDisplayButtons(); 
    });
}



function createQuestionElement(question) {
  const element = document.createElement("div");
  element.className =
    "question-element flex justify-between items-center p-4 border border-gray-300 rounded-md mb-2 bg-sky-600 text-white";
  element.innerHTML = `
        <div class="flex-1">
            <div><span class="font-semibold">Q:</span> ${question.text}</div>
            <div><span class="font-semibold">A:</span> ${
              question.correct_answer
            }</div>
        </div>
        <div class="actions">
            <button class="edit-button py-1 px-3 rounded bg-yellow-500 hover:bg-yellow-600 transition duration-300" data-question-id="${
              question.question_id
            }">
                Edit
            </button>
            <button class="delete-button py-1 px-3 rounded bg-red-500 hover:bg-red-600 transition duration-300 ml-2" data-question-id="${
              question.question_id
            }">
                Delete
            </button>

            <button class="ask-button py-1 px-3 rounded ${
              question.is_active ? "bg-red-600" : "bg-green-500"
            } hover:bg-green-600 transition duration-300 ml-2" data-question-id="${
    question.question_id
  }" data-is-active="${question.is_active}">
                ${question.is_active ? "Stop" : "Ask"}
            </button>
            <button class="display-button py-1 px-3 rounded bg-blue-500 hover:bg-blue-700 transition duration-300 ml-2" data-question-id="${
              question.question_id
            }">
                Display
            </button>
        </div>
    `;

  const askButton = element.querySelector(".ask-button");
  askButton.addEventListener("click", function () {
    const isActive = this.getAttribute("data-is-active") === "true";
    handleAskStopQuestion(question.question_id, !isActive, this);
  });

  element
    .querySelector(".delete-button")
    .addEventListener("click", function () {
      deleteQuestion(question.question_id);
    });

  const editButton = element.querySelector(".edit-button");
  editButton.addEventListener("click", function () {
    showEditQuestionModal(
      question.question_id,
      question.text,
      question.correct_answer
    );
  });

  return element;
}

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

function handleAskStopQuestion(questionId, isAsking, buttonElement) {
  const endpoint = `/class/${globalClassId}/question/${questionId}/ask`;

  buttonElement.disabled = true;

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": document
        .querySelector('meta[name="csrf-token"]')
        .getAttribute("content"),
    },
    body: JSON.stringify({ active: isAsking }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        buttonElement.textContent = isAsking ? "Stop" : "Ask";
        buttonElement.setAttribute("data-is-active", isAsking.toString());
        if (isAsking) {
          disableAllOtherAskButtons(buttonElement);
        } else {
          enableAllAskButtons();
        }
      } else {
        throw new Error(data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert(`An error occurred: ${error.message}`);
      buttonElement.textContent = isAsking ? "Ask" : "Stop";
      buttonElement.setAttribute("data-is-active", (!isAsking).toString());
    })
    .finally(() => {
      buttonElement.disabled = false;
    });
}


function disableAllOtherAskButtons(excludeButton) {
  document.querySelectorAll(".ask-button").forEach((btn) => {
    if (btn !== excludeButton) {
      btn.disabled = true;
    }
  });
}

function enableAllAskButtons() {
  document.querySelectorAll(".ask-button").forEach((btn) => {
    btn.disabled = false;
  });
}

function initializeQuestionEventListeners() {
  const askButtons = document.querySelectorAll(".ask-button");
  askButtons.forEach((button) => {
    const questionId = button.getAttribute("data-question-id");
    const isActive = button.getAttribute("data-is-active") === "true";
    button.addEventListener("click", () =>
      handleAskStopQuestion(questionId, !isActive, button)
    );
  });
}

function getClassIdFromUrl() {
  const urlParts = window.location.pathname.split("/");
  return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
}

function deleteQuestion(questionId) {
  if (!confirm("Are you sure you want to delete this question?")) return;
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  fetch(`/class/${globalClassId}/question/${questionId}/delete`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    credentials: "include",
  })
    .then((response) =>
      response.json().then((data) => ({ status: response.status, data: data }))
    )
    .then((result) => {
      if (result.status !== 200) {
        throw new Error(
          result.data.message ||
            "An error occurred while trying to delete the question."
        );
      }
      alert("Question successfully deleted.");
      fetchQuestionsAndDisplay(globalClassId);
    })
    .catch((error) => {
      console.error("Error deleting question:", error);
      alert(error.message);
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
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.success) {
          alert("Question successfully updated.");
          fetchQuestionsAndDisplay(globalClassId);
          document.getElementById("editQuestionModal").style.display = "none";
        } else {
          throw new Error("Failed to update the question.");
        }
      })
      .catch((error) => {
        console.error("Error updating question:", error);
        alert(`An error occurred: ${error.message}`);
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
        alert("Question successfully updated.");
        document.getElementById("editQuestionModal").style.display = "none";
        fetchQuestionsAndDisplay(globalClassId);
      } else {
        throw new Error("Failed to update the question.");
      }
    })
    .catch((error) => {
      console.error("Error updating question:", error);
      alert(`An error occurred: ${error.message}`);
    });
}

function setupDisplayButtons() {
  const buttons = document.querySelectorAll(".display-button");
  buttons.forEach(button => {
    const questionId = button.getAttribute("data-question-id");
    const isDisplayed = localStorage.getItem(`displayState-${questionId}`) === "true";
    button.textContent = isDisplayed ? "UnDisplay" : "Display";
    button.addEventListener("click", function() {
      const shouldDisplay = !isDisplayed; 
      toggleDisplay(questionId, shouldDisplay, button);
    });
  });
}

function updateQuestionDisplay(questionId, isDisplayed) {
  const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
  if (questionElement) {
    questionElement.style.display = isDisplayed ? 'block' : 'none'; 
  }
}

function handleDisplayClick() {
  const button = this;
  const questionId = button.getAttribute("data-question-id");
  const shouldDisplay = localStorage.getItem(`displayState-${questionId}`) !== "true";
  toggleDisplay(questionId, shouldDisplay, button);
}


async function toggleDisplay(questionId) {
  const button = document.querySelector(`[data-question-id="${questionId}"].display-button`);
  const endpoint = `/class/${globalClassId}/question/${questionId}/toggle_display`;
  const shouldDisplay = !button.classList.contains('active');

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
      },
      credentials: "include",
      body: JSON.stringify({ displayed: shouldDisplay })
    });

    const data = await response.json();

    if (data.success) {
      updateDisplayState(questionId, data.isDisplayed);
      alert(data.message);
    } else {
      alert(data.message); 
      if (data.displayedQuestionId) {
        highlightDisplayedQuestion(data.displayedQuestionId);
      }
    }
  } catch (error) {
    console.error("Error:", error);
    alert(`An error occurred: ${error.message}`);
  }
}

function highlightDisplayedQuestion(displayedQuestionId) {
  document.querySelectorAll('.display-button').forEach(button => {
    if (button.getAttribute('data-question-id') === displayedQuestionId) {
      button.classList.add('highlighted'); 
    } else {
      button.classList.remove('highlighted');
    }
  });
}


function updateDisplayState(questionId, isDisplayed) {
  const buttons = document.querySelectorAll(".display-button");
  buttons.forEach(btn => {
    btn.disabled = false; 
  });

  const targetButton = document.querySelector(`[data-question-id="${questionId}"].display-button`);
  targetButton.classList.toggle('active', isDisplayed);
  targetButton.textContent = isDisplayed ? "UnDisplay" : "Display";
}

