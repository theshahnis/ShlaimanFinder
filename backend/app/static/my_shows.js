document.addEventListener('DOMContentLoaded', function() {
    loadMyShows();
});

function loadMyShows() {
    fetch('/show/api/my-shows')
        .then(response => response.json())
        .then(data => {
            const shows = data.shows;
            renderMyShows(shows);
        });
}

function renderMyShows(shows) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = '';  // Clear the timetable

    shows.forEach(show => {
        const showDate = new Date(show.start_time);
        const endDate = new Date(show.end_time);

        const showElement = document.createElement('div');
        showElement.classList.add('show');
        showElement.innerHTML = `
            <span>${show.name}</span>
            <span>${showDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${endDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        `;
        timetable.appendChild(showElement);
    });
}
