document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("addQuestion").addEventListener("click", () => fetchContent("/add-question"));
  document.getElementById("classUsers").addEventListener("click", () => fetchContent("/userlist"));
  document.getElementById("feedback").addEventListener("click", () => fetchContent("/feedback"));
  document.getElementById("liveChat").addEventListener("click", () => fetchContent("/chat"));

  function fetchContent(endpoint) {
    fetch(endpoint)
      .then(response => response.text())
      .then(html => {
        document.getElementById("dashboardContent").innerHTML = html;
      })
      .catch(error => console.error("Error loading content:", error));
  }

  function initializeStartEndToggle() {
    const startClassBtn = document.getElementById("startClass");
    if (startClassBtn) {
      startClassBtn.addEventListener("click", function() {
        this.textContent = this.textContent.includes("Start") ? "End Class" : "Start Class";
        this.classList.toggle("bg-green-800");
        this.classList.toggle("bg-red-600");
      });
    }
  }

  initializeStartEndToggle();
});
