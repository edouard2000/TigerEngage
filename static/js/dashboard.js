document.addEventListener("DOMContentLoaded", () => {
  loadContent("/questions");
  document.getElementById("nav-chat").addEventListener("click", (e) => {
    e.preventDefault();
    loadContent("/chat");
  });

  document.getElementById("nav-question").addEventListener("click", (e) => {
    e.preventDefault();
    loadContent("/questions");
  });

  document.getElementById("nav-feedback").addEventListener("click", (e) => {
    e.preventDefault();
    loadContent("/feedback");
  });

  document.getElementById("nav-attendance").addEventListener("click", (e) => {
    e.preventDefault();
    loadContent("/attendance");
  });
});

function loadContent(url) {
  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      document.getElementById("content-area").innerHTML = html;
      setupDynamicContent();
    })
    .catch((error) => {
      console.error("Error loading content:", error);
    });
}

function setupDynamicContent() {
  const learnMoreBtn = document.getElementById("learnMoreBtn");
  const moreInfoContent = document.getElementById("moreInfoContent");

  if (learnMoreBtn) {
    learnMoreBtn.onclick = null;
    learnMoreBtn.addEventListener("click", () => {
      if (moreInfoContent.style.display === "none") {
        moreInfoContent.style.display = "block";
        learnMoreBtn.textContent = "Close";
      } else {
        moreInfoContent.style.display = "none";
        learnMoreBtn.textContent = "Learn More";
      }
    });
  }
}
