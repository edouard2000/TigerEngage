document.addEventListener("DOMContentLoaded", function () {
  const classId = getClassIdFromUrl();
  fetchContent("/userlist");
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

  fetchQuestionsAndRender(classId);
  initializeStartEndToggle();

  

  function fetchContent(endpoint) {
    fetch(endpoint)
      .then((response) => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          return response.json();
        }
        return response.text();
      })
      .then((data) => {
        if (typeof data === "object") {
          displayUserList(data);
        } else {
          document.getElementById("dashboardContent").innerHTML = data;
          if (endpoint === "/add-question") {
            initializeAddQuestionForm();
          }
        }
      })
      .catch((error) => {
        console.error("Error loading content:", error);
        document.getElementById("dashboardContent").innerHTML =
          "<p>Failed to load content. Please try again.</p>";
      });
  }





  function displayUserList(users) {
    const userListHTML = users
      .map((user) => `<div class="user-item">${user.name} - ${user.role}</div>`)
      .join("");
    document.getElementById(
      "dashboardContent"
    ).innerHTML = `<div>${userListHTML}</div>`;
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
        fetch(`/class/${classId}/add-question`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question_text: questionInput.value,
            answer_text: answerInput.value,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              questionForm.classList.add("hidden");
              createQuestionBtn.classList.remove("hidden");
              questionInput.value = "";
              answerInput.value = "";

              fetchQuestionsAndRender(classId);
            } else {
              alert("Failed to add the question. Please try again.");
            }
          })
          .catch((error) => {
            console.error("Error adding question:", error);
            alert(
              "Failed to add the question due to an error. Please try again."
            );
          });
      });
    }
  }

  // function createQuestionItem(question, answer) {
  //   const questionItem = document.createElement("div");
  //   questionItem.classList.add("question-item");
  //   questionItem.innerHTML = `
  //     <div class="question-text">
  //       <span class="font-bold">Question:</span> ${question}
  //       <span class="font-bold ml-4">Answer:</span> ${answer}
  //     </div>
  //   `;
  //   return questionItem;
  // }

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
});

function getClassIdFromUrl() {
  const pathSegments = window.location.pathname.split("/");
  const classId =
    pathSegments[pathSegments.length - 1] ||
    pathSegments[pathSegments.length - 2];
  return classId;
}

function fetchQuestionsAndRender(classId) {
  fetch(`/class/${classId}/questions`)
    .then((response) => response.json())
    .then((data) => {
      const questionsContainer = document.getElementById("questionsList");
      questionsContainer.innerHTML = "";
      if (data.success) {
        data.questions.forEach((question) => {
          const questionElement = document.createElement("div");
          questionElement.classList.add(
            "flex",
            "justify-between",
            "items-center",
            "bg-sky-600",
            "text-white",
            "p-4",
            "mb-2",
            "hover:bg-sky-700",
            "transition",
            "duration-300"
          );
          const questionAndAnswer = document.createElement("div");
          questionAndAnswer.innerHTML = `<span class="font-bold">Question:</span> ${question.text} <span class="ml-4 font-bold">Answer:</span> ${question.correct_answer}`;
          questionAndAnswer.classList.add("flex", "items-center");

          const actionsContainer = document.createElement("div");
          actionsContainer.classList.add("flex", "gap-2");

          const askButton = document.createElement("button");
          askButton.innerText = "Ask";
          askButton.classList.add(
            "bg-blue-600",
            "hover:bg-blue-700",
            "text-white",
            "py-1",
            "px-3",
            "rounded",
            "transition",
            "duration-300"
          );

          const editButton = document.createElement("button");
          editButton.innerText = "Edit";
          editButton.classList.add(
            "bg-green-600",
            "hover:bg-green-700",
            "text-white",
            "py-1",
            "px-3",
            "rounded",
            "transition",
            "duration-300"
          );

          const deleteButton = document.createElement("button");
          deleteButton.innerText = "Delete";
          deleteButton.classList.add(
            "bg-red-600",
            "hover:bg-red-700",
            "text-white",
            "py-1",
            "px-3",
            "rounded",
            "transition",
            "duration-300"
          );
          actionsContainer.appendChild(askButton);
          actionsContainer.appendChild(editButton);
          actionsContainer.appendChild(deleteButton);
          questionElement.appendChild(questionAndAnswer);
          questionElement.appendChild(actionsContainer);
          questionsContainer.appendChild(questionElement);
        });
      } else {
        console.error("Failed to fetch questions:", data.message);
        questionsContainer.innerHTML =
          "<p class='text-red-500'>Failed to fetch questions. Please try again.</p>";
      }
    })
    .catch((error) => {
      console.error("Error fetching questions:", error);
      questionsContainer.innerHTML =
        "<p class='text-red-500'>Error fetching questions. Please try again.</p>";
    });
}
