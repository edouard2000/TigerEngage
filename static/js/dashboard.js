document.addEventListener("DOMContentLoaded", () => {
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

// Button to control the learn more button(leanrMore and close)

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



function renderAttendanceCharts() {
  const scoreCanvas = document.getElementById("scoreChart");
  const attendanceCanvas = document.getElementById("attendanceChart");

  if (scoreCanvas && attendanceCanvas) {
    const scoreCtx = scoreCanvas.getContext("2d");
    const attendanceCtx = attendanceCanvas.getContext("2d");
    const scoreData = {
      datasets: [
        {
          data: [85.7, 14.3],
          backgroundColor: ["#4299E1", "#E2E8F0"],
          borderWidth: 0,
        },
      ],
    };
    const attendanceData = {
      datasets: [
        {
          data: [59.4, 40.6],
          backgroundColor: ["#4299E1", "#E2E8F0"],
          borderWidth: 0,
        },
      ],
    };

    new Chart(scoreCtx, {
      type: "doughnut",
      data: scoreData,
      options: {
        cutout: "90%",
        plugins: {
          legend: {
            display: false,
          },
        },
        maintainAspectRatio: false,
      },
    });

    new Chart(attendanceCtx, {
      type: "doughnut",
      data: attendanceData,
      options: {
        cutout: "90%",
        plugins: {
          legend: {
            display: false,
          },
        },
        maintainAspectRatio: false,
      },
    });
  }
}

function loadContent(url) {
  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      document.getElementById("content-area").innerHTML = html;
      setupDynamicContent();

      if (url.includes("/attendance")) {
        renderAttendanceCharts();
      }
    })
    .catch((error) => {
      console.error("Error loading content:", error);
    });
}
