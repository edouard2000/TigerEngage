let classId = null;

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOMContentLoaded");
  loadContent("/chat");
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
    classId = getClassIdFromUrl(); 
    loadContent(`/class/${classId}/feedback`);
  });

  document.getElementById("nav-attendance").addEventListener("click", (e) => {
    e.preventDefault();
    classId = getClassIdFromUrl(); 
    loadContent(`/attendance/${classId}/`);
});
});


function loadContent(url) {
  fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.text();
    })
    .then((html) => {
      document.getElementById("content-area").innerHTML = html;
      if (url.includes("/questions")) {
        fetchActiveQuestion(); 
      } else if (url.includes("/chat")) {
        fetchCurrentUserId();
      } 
    })
    .catch((error) => {
      console.error("Error loading content:", error);
      document.getElementById("content-area").innerHTML = `<p>Error loading content: ${error.message}</p>`;
    });
}
function fetchActiveQuestion() {
  classId = getClassIdFromUrl();
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

  classId = getClassIdFromUrl();
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