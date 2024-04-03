document.addEventListener("DOMContentLoaded", function () {
  fetchContent("/userlist");
  document.getElementById("addQuestion").addEventListener("click", () => fetchContent("/add-question"));
  document.getElementById("classUsers").addEventListener("click", () => fetchContent("/userlist"));
  document.getElementById("feedback").addEventListener("click", () => fetchContent("/feedback"));
  document.getElementById("liveChat").addEventListener("click", () => fetchContent("/chat"));

  initializeStartEndToggle();

  function fetchContent(endpoint) {
    fetch(endpoint)
      .then(response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          return response.json(); 
        }
        return response.text(); 
      })
      .then(data => {
        if (typeof data === 'object') { 
          displayUserList(data); 
        } else {
          document.getElementById("dashboardContent").innerHTML = data;
          if (endpoint === "/add-question") {
            initializeAddQuestionForm();
          }
        }
      })
      .catch(error => {
        console.error("Error loading content:", error);
        document.getElementById("dashboardContent").innerHTML = "<p>Failed to load content. Please try again.</p>";
      });
  }
  
  
  function displayUserList(users) {
    const userListHTML = users.map(user =>
      `<div class="user-item">${user.name} - ${user.role}</div>`
    ).join('');
    document.getElementById("dashboardContent").innerHTML = `<div>${userListHTML}</div>`;
  }
  

  function initializeAddQuestionForm() {
    const createQuestionBtn = document.getElementById("createQuestionBtn");
    const questionForm = document.getElementById("questionForm");
    const addQuestionBtn = document.getElementById("addQuestionBtn");
    if (createQuestionBtn) {
      createQuestionBtn.addEventListener("click", function () {
        questionForm.classList.remove("hidden");
        this.classList.add("hidden");
      });
    }
    if (addQuestionBtn) {
      addQuestionBtn.addEventListener("click", function () {
        const questionInput = document.getElementById("questionInput");
        const answerInput = document.getElementById("answerInput");

        fetch('/add-question', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            'question_text': questionInput.value,
            'answer_text': answerInput.value
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            const questionItem = createQuestionItem(questionInput.value, answerInput.value);
            document.getElementById("questionsList").appendChild(questionItem);
            questionForm.classList.add("hidden");
            createQuestionBtn.classList.remove("hidden");
            questionInput.value = "";
            answerInput.value = "";
          } else {
            alert("Failed to add the question. Please try again.");
          }
        })
        .catch(error => {
          console.error('Error adding question:', error);
        });
      });
    }
  }

  function createQuestionItem(question, answer) {
    const questionItem = document.createElement("div");
    questionItem.classList.add("question-item");
    questionItem.innerHTML = `
      <div class="question-text">
        <span class="font-bold">Question:</span> ${question}
        <span class="font-bold ml-4">Answer:</span> ${answer}
      </div>
    `;
    return questionItem;
  }

  function initializeStartEndToggle() {
    const startClassBtn = document.getElementById("startClass");
    if (startClassBtn) {
      startClassBtn.addEventListener("click", function () {
        this.textContent = this.textContent.includes("Start") ? "End Class" : "Start Class";
        this.classList.toggle("bg-green-800");
        this.classList.toggle("bg-red-600");
      });
    }
  }
});
