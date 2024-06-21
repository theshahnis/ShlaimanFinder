document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded');
    fetchSounds();

    document.getElementById('uploadForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData();
        const fileInput = document.getElementById('soundFile');
        formData.append('file', fileInput.files[0]);

        fetch('/sounds/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchSounds();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    document.getElementById('refreshSoundsButton').addEventListener('click', function() {
        console.log('Refresh button clicked');
        fetchSounds();
    });

    document.getElementById('playButton').addEventListener('click', function() {
        const soundSelect = document.getElementById('soundSelect');
        const selectedSound = soundSelect.value;
        if (selectedSound) {
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.src = `/sounds/get_sounds/${selectedSound}`;
            audioPlayer.play();
        } else {
            alert('Please select a sound');
        }
    });
});

function fetchSounds() {
    console.log('Fetching sounds...');
    fetch('/sounds/get_sounds')
        .then(response => response.json())
        .then(data => {
            console.log('Sounds fetched:', data);
            const soundSelect = document.getElementById('soundSelect');
            soundSelect.innerHTML = '<option value="">Select a sound</option>';
            data.sounds.forEach(sound => {
                const option = document.createElement('option');
                option.value = sound;
                option.textContent = sound;
                soundSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching sounds:', error);
        });
}
