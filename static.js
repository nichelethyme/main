// File upload handling
document.getElementById('dropZone').addEventListener('click', () => {
    document.getElementById('audioInput').click();
});

document.getElementById('audioInput').addEventListener('change', handleFiles);

// Drag and drop
document.getElementById('dropZone').addEventListener('dragover', (e) => {
    e.preventDefault();
    e.currentTarget.style.borderColor = 'var(--accent)';
});

document.getElementById('dropZone').addEventListener('drop', (e) => {
    e.preventDefault();
    e.currentTarget.style.borderColor = 'var(--border)';
    handleFiles({target: {files: e.dataTransfer.files}});
});

let uploadedFiles = [];

function handleFiles(event) {
    const files = Array.from(event.target.files);
    const formData = new FormData();
    
    files.forEach(file => {
        formData.append('audio_files', file);
    });

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            uploadedFiles.push(...data.files);
            displayAudioFiles();
        }
    });
}

function displayAudioFiles() {
    const container = document.getElementById('audioList');
    container.innerHTML = '';
    
    uploadedFiles.forEach((file, index) => {
        const div = document.createElement('div');
        div.className = 'audio-item';
        div.innerHTML = `
            <p>${file.name}</p>
            <audio controls>
                <source src="/static/uploads/${file.name}" type="audio/opus">
            </audio>
        `;
        container.appendChild(div);
    });
}

function spliceAudio() {
    const filePaths = uploadedFiles.map(f => f.path);
    
    fetch('/splice', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({files: filePaths})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Audio spliced! Check uploads folder.');
        }
    });
}

function saveSong() {
    const data = {
        title: prompt('Song title:') || 'Untitled',
        lyrics: document.getElementById('lyricsText').value,
        notes: document.getElementById('notesText').value,
        audio_files: uploadedFiles.map(f => f.name)
    };
    
    fetch('/save_song', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Song saved!');
        }
    });
}
