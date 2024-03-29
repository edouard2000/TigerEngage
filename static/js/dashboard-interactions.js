document.addEventListener('DOMContentLoaded', function() {
    fetchClassUsers();

    document.getElementById('addQuestion').addEventListener('click', () => fetchContent('/add-question'));
    document.getElementById('classUsers').addEventListener('click', fetchClassUsers);
    document.getElementById('feedback').addEventListener('click', () => fetchContent('/feedback'));
    document.getElementById('liveChat').addEventListener('click', () => fetchContent('/chat'));

    function fetchClassUsers() {
        fetchContent('/userlist');
    }

    function fetchContent(endpoint) {
        fetch(endpoint)
        .then(response => response.text())
        .then(html => {
            document.getElementById('dashboardContent').innerHTML = html;
            // After loading, check if we need to initialize form functionality
            if (endpoint === '/add-question') {
                initializeAddQuestionForm();
            }
        })
        .catch(error => {
            console.error('Error loading content:', error);
            document.getElementById('dashboardContent').innerHTML = '<p>Failed to load content. Please try again.</p>';
        });
    }

    function initializeAddQuestionForm() {
        const createQuestionBtn = document.getElementById('createQuestionBtn');
        const questionForm = document.getElementById('questionForm');
        const addQuestionBtn = document.getElementById('addQuestionBtn');
        const questionsList = document.getElementById('questionsList');

        if (createQuestionBtn) {
            createQuestionBtn.addEventListener('click', function() {
                this.classList.add('hidden');
                questionForm.classList.remove('hidden');
            });
        }

        if (addQuestionBtn) {
            addQuestionBtn.addEventListener('click', function() {
                const questionInput = document.getElementById('questionInput').value;
                const answerInput = document.getElementById('answerInput').value;

                createQuestionBtn.classList.remove('hidden');
                questionForm.classList.add('hidden');

                document.getElementById('questionInput').value = '';
                document.getElementById('answerInput').value = '';

                const questionItem = document.createElement('div');
                questionItem.classList.add('flex', 'justify-between', 'items-center', 'my-2');
                questionItem.innerHTML = `
                    <div>
                        <span class="font-bold">Question:</span> ${questionInput}
                        <span class="font-bold ml-4">Answer:</span> ${answerInput}
                    </div>
                    <div>
                        <button class="bg-blue-500 text-white py-1 px-3 rounded hover:bg-blue-600 transition duration-300">Edit</button>
                        <button class="bg-green-500 text-white py-1 px-3 rounded hover:bg-green-600 transition duration-300">Ask</button>
                    </div>
                `;
                questionsList.appendChild(questionItem);
            });
        }
    }
});
