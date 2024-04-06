document.addEventListener("DOMContentLoaded", function () {
  // Initialize event listeners for the navigation
  document
    .getElementById("addQuestion")
    .addEventListener("click", () => fetchContent("/add-question"));
  document.getElementById("classUsers").addEventListener("click", function () {
    const classId = this.getAttribute("data-class-id");
    fetchContent(`/class/${classId}/userlist`);
  });
  document.getElementById("feedback").addEventListener("click", function () {
    const classId = this.getAttribute("data-class-id");
    fetchContent(`/class/${classId}/feedback`);
  });
  document
    .getElementById("liveChat")
    .addEventListener("click", () => fetchContent("/chat"));

  // Fetch content for the dashboard
  function fetchContent(endpoint) {
    fetch(endpoint)
      .then((response) => response.text())
      .then((html) => {
        const dashboardContent = document.getElementById("dashboardContent");
        dashboardContent.innerHTML = html;

        if (endpoint === "/add-question") {
          initializeQuestionFormEventListeners();
        }
      })
      .catch((error) => console.error("Error loading content:", error));
  }

  // Initialize the toggle for Start/End class
  function initializeStartEndToggle() {
    const startClassBtn = document.getElementById("startClass");
    if (startClassBtn) {
      startClassBtn.addEventListener("click", function () {
        this.textContent = this.textContent.includes("Start")
          ? "End Class"
          : "Start Class";
        this.classList.toggle("bg-green-800");
        this.classList.toggle("bg-red-600");
      });
    }
  }

  // Initialize toggle functionality when DOM is loaded
  initializeStartEndToggle();

  // Handle question form visibility and event listeners
  function initializeQuestionFormEventListeners() {
    let csrfToken = document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");
    const classId = getClassIdFromUrl();

    // Toggle the visibility of the create question button and form
    const createQuestionBtn = document.getElementById("createQuestionBtn");
    const questionForm = document.getElementById("questionForm");

    if (createQuestionBtn && questionForm) {
      createQuestionBtn.addEventListener("click", function () {
        questionForm.classList.toggle("hidden");
        createQuestionBtn.classList.toggle("hidden");
      });
    }

    // Add question logic
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

  // Fetch questions and create their elements
  function fetchQuestionsAndDisplay(classId) {
    fetch(`/class/${classId}/questions`)
      .then((response) => response.json())
      .then((data) => {
        const questionsContainer = document.getElementById("questionsList");
        questionsContainer.innerHTML = "";

        if (data.questions && data.questions.length > 0) {
          data.questions.forEach((question) => {
            const questionElement = createQuestionElement(question);
            questionsContainer.appendChild(questionElement);
          });
        } else {
          questionsContainer.innerHTML = `<p class="text-gray-700">No questions created for this class yet.</p>`;
        }
      })
      .catch((error) => console.error("Error fetching questions:", error));
  }

 // Simplified createQuestionElement function
function createQuestionElement(question) {
  const element = document.createElement("div");
  element.className = "flex justify-between items-center p-4 border border-gray-300 rounded-md mb-2 bg-sky-600 hover:bg-sky-950";

  // HTML structure for the question element
  element.innerHTML = `
    <div class="flex-1 mr-4 text-white">
      <span class="font-semibold">Q:</span> ${question.text}
      <span class="font-semibold">A:</span> ${question.correct_answer}
    </div>
    <div class="flex space-x-2">
      <button class="ask-button bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded">Ask</button>
      <button class="edit-button bg-green-500 hover:bg-green-700 text-white py-1 px-3 rounded">Edit</button>
      <button class="summary-button bg-yellow-500 hover:bg-yellow-700 text-white py-1 px-3 rounded">Get Summary</button>
      <button class="delete-button bg-red-500 hover:bg-red-700 text-white py-1 px-3 rounded">Delete</button>
    </div>
  `;

  // Ask/Stop button functionality
  const askButton = element.querySelector(".ask-button");
  askButton.addEventListener("click", function () {
    const isAsking = this.textContent === "Ask";
    this.textContent = isAsking ? "Stop" : "Ask";
    this.classList.toggle("bg-blue-500", !isAsking);
    this.classList.toggle("bg-red-500", isAsking);
    // Optionally: Call a function to handle the ask/stop action
    handleAskStopQuestion(question.question_id, isAsking);
  });

    // Edit button functionality
    const editButton = element.querySelector(".edit-button");
    editButton.addEventListener("click", function () {
      // Redirect to edit question page/form
      window.location.href = `/class/${classId}/edit-question/${question.question_id}`;
    });
  
    // Delete button functionality
    const deleteButton = element.querySelector(".delete-button");
    deleteButton.addEventListener("click", function () {
      if (confirm("Are you sure you want to delete this question?")) {
        fetch(`/class/${classId}/delete-question/${question.question_id}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
          },
        })
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to delete question');
          }
          return response.json();
        })
        .then(data => {
          if (data.success) {
            element.remove(); 
          } else {
            console.error("Error deleting question:", data.message);
          }
        })
        .catch(error => {
          console.error("Error deleting question:", error);
        });
      }
    });

  // Summary similarly
  
  return element;
}


// Function to handle the ask/stop action for a question
function handleAskStopQuestion(questionId, isAsking) {
  const action = isAsking ? "start" : "stop";
  fetch(`/class/${classId}/question/${questionId}/${action}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
    },
    body: JSON.stringify({ active: isAsking }),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to update question status');
    }
    return response.json();
  })
  .then(data => {
    if (!data.success) {
      console.error("Error handling ask/stop question:", data.message);
    }
  })
  .catch(error => {
    console.error("Error handling ask/stop question:", error);
  });
}



  // Get the class ID from the URL
  function getClassIdFromUrl() {
    const urlParts = window.location.pathname.split("/");
    return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
  }
});

document.getElementById("classUsers").addEventListener("click", function () {
  const classId = this.getAttribute("data-class-id");
  fetchContent(`/class/${classId}/userlist`);
});
