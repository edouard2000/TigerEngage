function getClassIdFromUrl() {
    const urlPath = window.location.pathname;
    const pathSegments = urlPath.split('/');
    return pathSegments[pathSegments.length - 1];
}

function checkAndShowFeedbackModal(classId) {
    fetch(`/check_feedback_modal/${classId}`)
        .then(response => response.json())
        .then(data => {
            if (data.showModal) {
                displayFeedbackModal();
            }
        })
        .catch(error => console.error('Error checking modal display status:', error));
}

function displayFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    modal.classList.remove('hidden');
}

function setupFormSubmission(classId) {
    const feedbackForm = document.getElementById('feedbackForm');
    feedbackForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        const rating = formData.get('rating');
        const comment = formData.get('comment');

        fetch('/submit_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                class_session_id: classId,
                class_id: classId,
                student_id: studentId, 
                rating: rating,
                comment: comment
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Feedback submitted successfully!');
                const modal = document.getElementById('feedbackModal');
                modal.classList.add('hidden');
            } else {
                alert(data.message || 'Failed to submit feedback.');
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
            alert('Failed to submit feedback due to network error.');
        });
    });
}

document.querySelector('.modal-close').addEventListener('click', function () {
    const modal = document.getElementById('feedbackModal');
    modal.classList.add('hidden');
});

document.addEventListener("DOMContentLoaded", function () {
    const classId = getClassIdFromUrl();
    checkAndShowFeedbackModal(classId);
    setupFormSubmission(classId);
});
