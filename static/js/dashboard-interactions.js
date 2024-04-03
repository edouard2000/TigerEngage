document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("addQuestion")
    .addEventListener("click", () => fetchContent("/add-question"));
  document
    .getElementById("classUsers")
    .addEventListener("click", () => fetchContent("/userlist"));
  document
    .getElementById("feedback")
    .addEventListener("click", () => fetchContent("/feedback"));
  document
    .getElementById("liveChat")
    .addEventListener("click", () => fetchContent("/chat"));



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

  initializeStartEndToggle();
});

function initializeQuestionFormEventListeners() {
  const classId = getClassIdFromUrl();

  const createQuestionBtn = document.getElementById("createQuestionBtn");
  if (createQuestionBtn) {
    createQuestionBtn.addEventListener("click", function () {
      document.getElementById("questionForm").classList.toggle("hidden");
    });
  }

  const addQuestionBtn = document.getElementById("addQuestionBtn");
  if (addQuestionBtn) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    console.log("csrf token: " + csrfToken);
    addQuestionBtn.addEventListener("click", function () {
      const questionInput = document.getElementById("questionInput");
      const answerInput = document.getElementById("answerInput");
      console.log(`/class/${classId}/add-question`);
      fetch(`/class/${classId}/add-question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        "X-CSRFToken": csrfToken,
        body: JSON.stringify({
          question_text: questionInput.value,
          correct_answer: answerInput.value,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            fetchQuestionsAndDisplay(classId);
            questionInput.value = "";
            answerInput.value = "";
          } else {
            alert("Failed to add the question. Please try again.");
          }
        })
        .catch((error) => console.error("Error adding question:", error));
    });
  }

  fetchQuestionsAndDisplay(classId);
}

function fetchQuestionsAndDisplay(classId) {
  fetch(`/class/${classId}/questions`)
    .then((response) => response.json())
    .then((data) => {
      const questionsContainer = document.getElementById("questionsList");
      questionsContainer.innerHTML = "";

      if (data.questions && data.questions.length > 0) {
        data.questions.forEach((question) => {
          questionsContainer.appendChild(createQuestionElement(question));
        });
      } else {
        questionsContainer.innerHTML = `<p class="text-gray-700">No questions created for this class yet.</p>`;
      }
    })
    .catch((error) => console.error("Error fetching questions:", error));
}

function createQuestionElement(question) {
  const element = document.createElement("div");
  element.classList.add(
    "flex",
    "justify-between",
    "items-center",
    "p-4",
    "border",
    "border-gray-300",
    "rounded-md",
    "mb-2"
  );
  element.innerHTML = `
   <div class="flex">
      <div>
        <span class="font-semibold">Q:</span> ${question.text} - 
        <span class="font-semibold">A:</span> ${question.correct_answer}
      </div>

      <div class="flex  space-x-2">
        <button class="bg-blue-500 hover:bg-blue-700 text-white py-1 px-3 rounded">Ask</button>
        <button class="bg-green-500 hover:bg-green-700 text-white py-1 px-3 rounded">Edit</button>
        <button class="bg-yellow-500 hover:bg-yellow-700 text-white py-1 px-3 rounded">Get Summary</button>
        <button class="bg-red-500 hover:bg-red-700 text-white py-1 px-3 rounded">Delete</button>
      </div>

   </div>
  `;
  return element;
}

function getClassIdFromUrl() {
  const urlParts = window.location.pathname.split("/");
  return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2];
}
