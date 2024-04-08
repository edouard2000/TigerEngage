let globalClassId = null;

document.addEventListener("DOMContentLoaded", function () {
    globalClassId = getClassIdFromUrl();
    document.getElementById("addQuestion").addEventListener("click", () => fetchContent("/add-question"));
    document.getElementById("classUsers").addEventListener("click", function () {
        const classId = this.getAttribute("data-class-id");
        fetchContent(`/class/${classId}/userlist`);
    });
    document.getElementById("feedback").addEventListener("click", function () {
        const classId = this.getAttribute("data-class-id");
        fetchContent(`/class/${classId}/feedback`);
    });
    document.getElementById("liveChat").addEventListener("click", () => fetchContent("/chat"));

    initializeStartEndToggle();
    initializeQuestionFormEventListeners();
    fetchQuestionsAndDisplay(globalClassId);
});

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



  function initializeQuestionFormEventListeners() {
    let csrfToken = document
      .querySelector('meta[name="csrf-token"]')
      .getAttribute("content");
      console.log(` classid:${globalClassId}`)
    const classId = globalClassId;
    console.log(`this is a classid: ${classId}`);



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
  .then(response => response.json())
  .then(data => {
      const questionsContainer = document.getElementById("questionsList");
      questionsContainer.innerHTML = "";
      if (data.questions && data.questions.length > 0) {
          data.questions.forEach(question => {
              const questionElement = createQuestionElement(question);
              questionsContainer.appendChild(questionElement);
          });
          initializeQuestionEventListeners();
      } else {
          questionsContainer.innerHTML = "<p>No questions found for this class.</p>";
      }
  })
  .catch(error => {
      console.error("Error fetching questions:", error);
  });
}

function createQuestionElement(question) {
  const element = document.createElement("div");
  element.className = "question-element p-4 border border-gray-300 rounded-md mb-2 bg-sky-600 hover:bg-sky-950 text-white";
  element.innerHTML = `
      <div class="flex-1 mr-4">
          <span class="font-semibold">Q:</span> ${question.text}
          <span class="font-semibold">A:</span> ${question.correct_answer}
      </div>
      <button class="ask-button py-1 px-3 rounded" data-question-id="${question.question_id}" data-is-active="${question.is_active}">
          ${question.is_active ? "Stop" : "Ask"}
      </button>
  `;

  const askButton = element.querySelector(".ask-button");
  askButton.addEventListener("click", function () {
      const isActive = this.getAttribute("data-is-active") === "true";
      handleAskStopQuestion(question.question_id, !isActive, this);
  });

  return element;
}


function handleAskStopQuestion(questionId, isAsking, buttonElement) {
  const endpoint = `/class/${globalClassId}/question/${questionId}/ask`;

  buttonElement.disabled = true; 

  fetch(endpoint, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
      },
      body: JSON.stringify({ active: isAsking }),
  })
  .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
  })
  .then(data => {
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
  .catch(error => {
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
  document.querySelectorAll('.ask-button').forEach(btn => {
      if (btn !== excludeButton) {
          btn.disabled = true; 
      }
  });
}

function enableAllAskButtons() {
  document.querySelectorAll('.ask-button').forEach(btn => {
      btn.disabled = false; 
  });
}



function initializeQuestionEventListeners() {
  const askButtons = document.querySelectorAll(".ask-button");
  askButtons.forEach(button => {
      const questionId = button.getAttribute("data-question-id");
      const isActive = button.getAttribute("data-is-active") === "true";
      button.addEventListener("click", () => handleAskStopQuestion(questionId, !isActive, button));
  });
}

function getClassIdFromUrl() {
  const urlParts = window.location.pathname.split("/");
  return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
}


