document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("class-search");
    const searchResults = document.getElementById("search-results");
    const enrolledClassesContainer = document.getElementById("enrolled-classes");
  
    searchInput.addEventListener("input", handleSearchInput);
  
    fetchEnrolledClasses();
  
    function handleSearchInput() {
      const query = searchInput.value.trim();
      if (query.length < 3) {
        searchResults.style.display = "none";
        return;
      }
      searchResults.style.display = "block";
      fetch(`/search_classes?search=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          renderSearchResults(data.classes);
        })
        .catch((error) => console.error("Search Error:", error));
    }
  
    function renderSearchResults(classes) {
      searchResults.innerHTML = "";
      classes.forEach((cls) => {
        const classDiv = document.createElement("div");
        classDiv.className = "flex justify-center items-center p-4 border-b border-gray-200";
        classDiv.innerHTML = `<span class="font-semibold">${cls.name}</span> - <span>${cls.instructor}</span>`;
  
        const enrollButton = document.createElement("button");
        enrollButton.className = "ml-2 bg-sky-950 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded";
        enrollButton.textContent = "Enroll";
        enrollButton.addEventListener("click", () => enrollInClass(cls.id));
  
        classDiv.appendChild(enrollButton);
        searchResults.appendChild(classDiv);
      });
    }
  
    function enrollInClass(classId) {
      fetch('/enroll_in_class', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({ class_id: classId })
      })
      .then(response => response.json())
      .then(data => {
        alert(data.message);
        if (data.success) {
          searchInput.value = '';
          searchResults.innerHTML = ''; 
          fetchEnrolledClasses();
        }
      })
      .catch(error => console.error('Enrollment Error:', error));
    }
  
    function fetchEnrolledClasses() {
      fetch("/get_enrolled_classes")
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            renderEnrolledClasses(data.classes);
          } else {
            enrolledClassesContainer.innerHTML = "You are not enrolled in any classes.";
          }
        })
        .catch((error) => {
          console.error("Error fetching enrolled classes:", error);
          enrolledClassesContainer.innerHTML = "Error loading enrolled classes.";
        });
    }
  
    function renderEnrolledClasses(classes) {
        enrolledClassesContainer.innerHTML = '';
        classes.forEach(cls => {
            const classDiv = document.createElement('div');
            classDiv.className = 'bg-sky-600 mb-4 rounded-md shadow hover:bg-sky-700 transition ease-in-out duration-150';
            
            const classContentDiv = document.createElement('div');
            classContentDiv.className = 'flex flex-col sm:flex-row items-center justify-center sm:justify-between px-4 py-4 sm:px-6 w-full';

    
            const classInfoDiv = document.createElement('div');
            classInfoDiv.className = 'mb-2 sm:mb-0';
            classInfoDiv.innerHTML = `
                <p class="text-lg sm:text-xl font-bold text-white truncate">${cls.name}</p>
                <p class="text-xs sm:text-sm text-gray-300">${cls.instructor}</p>
            `;
    
            const classActionsDiv = document.createElement('div');
            classActionsDiv.className = 'flex-shrink-0 space-x-2';
            classActionsDiv.style.minWidth = '240px';
    
            const removeButton = document.createElement('button');
            removeButton.onclick = () => unenrollFromClass(cls.id);
            removeButton.className = 'bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition ease-in-out duration-150';
            removeButton.textContent = 'Remove';
    
        
            const checkInButton = document.createElement('button');
            checkInButton.setAttribute('data-class-id', cls.id); 
            checkInButton.className = cls.is_active ? 'bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition ease-in-out duration-150' : 'bg-gray-500 text-white font-bold py-2 px-4 rounded';
            checkInButton.textContent = cls.is_active ? 'Check In' : 'Not Started';
            checkInButton.disabled = !cls.is_active; 
            checkInButton.addEventListener('click', () => checkInToClass(cls.id));
    
            classActionsDiv.appendChild(removeButton);
            classActionsDiv.appendChild(checkInButton);
    
            classContentDiv.appendChild(classInfoDiv);
            classContentDiv.appendChild(classActionsDiv);
    
            classDiv.appendChild(classContentDiv);
    
            enrolledClassesContainer.appendChild(classDiv);
        });
    }
    
    
  
    window.unenrollFromClass = function (classId) {
      fetch('/unenroll_from_class', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({ class_id: classId })
      })
      .then(response => response.json())
      .then(data => {
        alert(data.message);
        if (data.success) {
          fetchEnrolledClasses();
        }
      })
      .catch(error => console.error('Unenrollment Error:', error));
    };
  });
  


  function checkInToClass(classId) {
    fetch(`/class/${classId}/check_in`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
      },
      body: JSON.stringify({ class_id: classId })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        window.location.href = data.redirectUrl;
      } else {
        displayAlert(data.message, 'error');
      }
    })
    .catch(error => {
      console.error('Error checking in:', error);
      displayAlert('An error occurred during check-in.', 'error');
    });
  }
  
  function updateCheckInButton(classId) {
    const checkInButton = document.querySelector(`[data-class-id="${classId}"]`);
    if (checkInButton) {
      checkInButton.disabled = true;
      checkInButton.textContent = 'Checked In';
      checkInButton.classList.replace('bg-green-500', 'bg-gray-500');
      checkInButton.classList.replace('hover:bg-green-700', 'hover:bg-gray-700');
    }
  }
  
  function displayAlert(message, type) {
    const alertBox = document.createElement('div');
    alertBox.textContent = message;
    alertBox.className = `alert ${type === 'success' ? 'alert-success' : 'alert-error'}`;
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
      existingAlert.replaceWith(alertBox);
    } else {
      const mainContainer = document.querySelector('main');
      mainContainer.insertBefore(alertBox, mainContainer.firstChild);
    }
    setTimeout(() => {
      alertBox.remove();
    }, 5000);
  }
 
  document.querySelectorAll('.check-in').forEach(button => {
    button.addEventListener('click', () => {
      const sessionId = button.dataset.sessionId;
      checkInToClass(sessionId);
    });
  });