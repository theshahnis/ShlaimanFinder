document.addEventListener('DOMContentLoaded', function() {
    loadMyShows();
});

function loadMyShows() {
    fetch('/show/api/my-shows')
        .then(response => response.json())
        .then(data => {
            const shows = data.shows;
            renderMyShows(shows);
        })
        .catch(error => console.error("Error fetching user shows:", error));
}

function renderMyShows(shows) {
    const timetable = document.querySelector('.my-shows-timetable'); // Use specific class for my-shows
    timetable.innerHTML = ''; // Clear the timetable

    let lastDate = null;

    shows.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

    shows.forEach(show => {
        const showDate = new Date(show.start_time);
        const endDate = new Date(show.end_time);
        const showDateString = showDate.toLocaleDateString();

        if (showDateString !== lastDate) {
            lastDate = showDateString;
            const dateHeader = document.createElement('h2');
            dateHeader.textContent = showDateString;
            timetable.appendChild(dateHeader);
        }

        const showElement = document.createElement('div');
        showElement.classList.add('show');
        showElement.setAttribute('data-show-id', show.id);
        showElement.innerHTML = `
            <span class="show-name">${show.name}</span>
            <span class="show-time">${showDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            <span class="show-stage">${show.stage}</span>
        `;
        timetable.appendChild(showElement);
    });
}
