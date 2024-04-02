// learn-more.js - Refactored
function setupLearnMoreButton() {
    const learnMoreBtn = document.getElementById("learnMoreBtn");
    const moreInfoContent = document.getElementById("moreInfoContent");

    if (learnMoreBtn && moreInfoContent) {
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
