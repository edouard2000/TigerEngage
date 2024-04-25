document.addEventListener("DOMContentLoaded", () => {
  loadContent("/chat");
  console.log("Test 5")

  document.getElementById("nav-question").addEventListener("click", (e) => {
    e.preventDefault();
    loadContent("/questions");
  });

  document.getElementById("nav-chat").addEventListener("click", (e) => {
    e.preventDefault();
    loadContent("/chat");
  });

  document.getElementById("nav-feedback").addEventListener("click", (e) => {
    e.preventDefault();
    const classId = getClassIdFromUrl(); 
    loadContent(`/class/${classId}/feedback`);
  });

  document.getElementById("nav-attendance").addEventListener("click", (e) => {
    e.preventDefault();
    const classId = getClassIdFromUrl(); 
    loadContent(`/attendance/${classId}/`);
  });
});


function loadContent(url) {
  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      document.getElementById("content-area").innerHTML = html;
      if (url.endsWith("/questions")) {
        fetchActiveQuestion();
      }
      setupDynamicContent();
    })
    .catch((error) => {
      console.error("Error loading content:", error);
    });
}

function fetchActiveQuestion() {
  const classId = getClassIdFromUrl();
  fetch(`/class/${classId}/active-question`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.question) {
        displayActiveQuestion(data.question);
      } else {
        displayNoActiveQuestion();
      }
    })
    .catch((error) => {
      console.error("Error fetching active question:", error);
    });
}

function displayActiveQuestion(question) {
  const questionTextElement = document.getElementById("question-text");
  questionTextElement.textContent = question.text;

  const answerForm = document.getElementById("answer-form");
  answerForm.onsubmit = (e) => {
    e.preventDefault();
    submitAnswer(question.question_id);
  };
}

function displayNoActiveQuestion() {
  const questionTextElement = document.getElementById("question-text");
  questionTextElement.textContent = "No active question at the moment.";
}

function submitAnswer(questionId) {
  const answerText = document.getElementById("student-answer").value.trim();
  if (answerText === "") {
    alert("Please enter your answer before submitting.");
    return;
  }

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");

  const classId = getClassIdFromUrl();
  fetch(`/class/${classId}/submit-answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: JSON.stringify({ questionId, answerText }),
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Answer submitted successfully.");
        document.getElementById("student-answer").value = "";
      } else {
        alert(data.message);
      }
    })
    .catch((error) => {
      console.error("Error submitting answer:", error);
      alert("An error occurred while submitting your answer.");
    });
}

function getClassIdFromUrl() {
  const urlParts = window.location.pathname.split("/");
  const lastIndex = urlParts.length - 1;
  return urlParts[lastIndex] || urlParts[lastIndex - 1];
}
