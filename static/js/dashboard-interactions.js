document.addEventListener("DOMContentLoaded", function () {
  fetchClassUsers();

  document.getElementById("addQuestion").addEventListener("click", () => fetchContent("/add-question"));
  document.getElementById("classUsers").addEventListener("click", fetchClassUsers);
  document.getElementById("feedback").addEventListener("click", () => fetchContent("/feedback"));
  document.getElementById("liveChat").addEventListener("click", () => fetchContent("/chat"));

  // Initialize Start/End button toggle
  initializeStartEndToggle();

  function fetchClassUsers() {
    fetchContent("/userlist");
  }

  function fetchContent(endpoint) {
    fetch(endpoint)
      .then((response) => response.text())
      .then((html) => {
        document.getElementById("dashboardContent").innerHTML = html;
        // Initialize form functionality if the Add Question page is loaded
        if (endpoint === "/add-question") {
          initializeAddQuestionForm();
        }
      })
      .catch((error) => {
        console.error("Error loading content:", error);
        document.getElementById("dashboardContent").innerHTML =
          "<p>Failed to load content. Please try again.</p>";
      });
  }

  function initializeAddQuestionForm() {
    const createQuestionBtn = document.getElementById("createQuestionBtn");
    const questionForm = document.getElementById("questionForm");
    const addQuestionBtn = document.getElementById("addQuestionBtn");
    const questionsList = document.getElementById("questionsList");

    if (createQuestionBtn) {
      createQuestionBtn.addEventListener("click", function () {
        this.classList.add("hidden");
        questionForm.classList.remove("hidden");
      });
    }

    if (addQuestionBtn) {
      addQuestionBtn.addEventListener("click", function () {
        const questionInput = document.getElementById("questionInput").value;
        const answerInput = document.getElementById("answerInput").value;

        // Reset visibility and form values
        createQuestionBtn.classList.remove("hidden");
        questionForm.classList.add("hidden");
        document.getElementById("questionInput").value = "";
        document.getElementById("answerInput").value = "";

        // Add question to the list
        const questionItem = document.createElement("div");
        questionItem.classList.add("question-item");
        questionItem.innerHTML = `
          <div class="question-text">
            <span class="font-bold">Question:</span> ${questionInput}
            <span class="font-bold ml-4">Answer:</span> ${answerInput}
          </div>
          <div class="button-container">
            <button class="bg-blue-500 text-white py-1 px-3 rounded hover:bg-blue-600 transition duration-300">Edit</button>
            <button class="bg-green-500 text-white py-1 px-3 rounded hover:bg-green-600 transition duration-300">Ask</button>
          </div>
        `;
        questionsList.appendChild(questionItem);
      });
    }
  }

  function initializeStartEndToggle() {
    const startClassBtn = document.getElementById("startClass");
    if (startClassBtn) {
      startClassBtn.addEventListener("click", function () {
        if (this.textContent.includes("Start")) {
          this.textContent = "End Class";
          this.classList.remove("bg-green-800"); // Assuming "Start" uses bg-green-800
          this.classList.add("bg-red-600"); // Switch to a different color for "End"
        } else {
          this.textContent = "Start Class";
          this.classList.remove("bg-red-600"); // Remove "End" color
          this.classList.add("bg-green-800"); // Revert to original "Start" color
        }
      });
    }
  }
});
