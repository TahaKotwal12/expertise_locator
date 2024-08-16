document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadMessage = document.getElementById('uploadMessage');
    const searchQuery = document.getElementById('searchQuery');
    const searchButton = document.getElementById('searchButton');
    const searchResults = document.getElementById('searchResults');
    const fileInput = document.getElementById('resumeFile');
    const fileLabel = document.querySelector('.file-input-wrapper label span');
    const uploadAnimation = document.querySelector('.upload-animation');

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            fileLabel.textContent = e.target.files[0].name;
        } else {
            fileLabel.textContent = 'Choose a file';
        }
    });

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        uploadAnimation.style.display = 'flex';
        uploadMessage.textContent = '';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadAnimation.style.display = 'none';
            if (data.success) {
                uploadMessage.textContent = data.success;
                uploadMessage.style.color = 'green';
                uploadMessage.classList.add('fade-in');
            } else {
                uploadMessage.textContent = data.error || 'An unknown error occurred';
                uploadMessage.style.color = 'red';
                uploadMessage.classList.add('fade-in');
            }
            setTimeout(() => {
                uploadMessage.classList.remove('fade-in');
            }, 300);
        })
        .catch(error => {
            uploadAnimation.style.display = 'none';
            console.error('Error:', error);
            uploadMessage.textContent = 'An error occurred while uploading the file: ' + error.message;
            uploadMessage.style.color = 'red';
            uploadMessage.classList.add('fade-in');
            setTimeout(() => {
                uploadMessage.classList.remove('fade-in');
            }, 300);
        });
    });

    searchButton.addEventListener('click', performSearch);
    searchQuery.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const query = searchQuery.value;
        if (query.trim() === '') {
            alert('Please enter a search query');
            return;
        }

        searchResults.innerHTML = '<div class="loading">Searching...</div>';

        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            searchResults.innerHTML = '';
            if (data.length === 0) {
                searchResults.innerHTML = '<p>No results found.</p>';
                return;
            }
            data.forEach((result, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                resultItem.style.animationDelay = `${index * 0.1}s`;
                resultItem.innerHTML = `
                    <h3>${result.name}</h3>
                    <p>Similarity: ${(result.similarity * 100).toFixed(2)}%</p>
                `;
                searchResults.appendChild(resultItem);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            searchResults.innerHTML = '<p>An error occurred while searching.</p>';
        });
    }
});