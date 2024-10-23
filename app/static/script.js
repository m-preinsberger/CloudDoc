const dropArea = document.getElementById('drop-area');
const fileList = document.getElementById('file-list');
const progressBar = document.getElementById('progress-bar');
const commitBtn = document.getElementById('commit-btn');
const downloadLinkDiv = document.getElementById('download-link');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
});

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (!fileList) {
        console.error('fileList element not found');
        return;
    }

    fileList.innerHTML = ''; // Clear the file list

    if (!files || !files.length) {
        console.error('No files to handle');
        return;
    }

    ([...files]).forEach(file => {
        const li = document.createElement('li');
        li.textContent = file.name;
        fileList.appendChild(li);
        uploadFile(file);
    });
}

function uploadFile(file) {
    const url = '/upload';
    const formData = new FormData();
    formData.append('file', file);
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.value = percentComplete;
        }
    });
    xhr.onload = () => {
        if (xhr.status === 200) {
            console.log('File uploaded successfully');
            fetchFiles(); // Refresh the file list after upload
        } else {
            console.error('File upload failed');
        }
    };
    xhr.send(formData);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchFiles();
});

function fetchFiles() {
    fetch('/files')
        .then(response => response.json())
        .then(data => {
            const files = data.files;
            if (!Array.isArray(files)) {
                console.error('files is not an array');
                return;
            }
            fileList.innerHTML = ''; // Clear the file list
            files.forEach(file => {
                const li = document.createElement('li');
                li.textContent = file;
                fileList.appendChild(li);
            });
        })
        .catch(error => console.error('Error fetching files:', error));
}

commitBtn.addEventListener('click', () => {
    fetch('/commit', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            const downloadUrl = data.download_url;
            downloadLinkDiv.innerHTML = `<a href="${downloadUrl}" target="_blank">Download All Files</a>`;
        })
        .catch(error => console.error('Error committing files:', error));
});