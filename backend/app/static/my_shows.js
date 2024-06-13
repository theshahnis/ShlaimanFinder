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
            <button class="whos-going">Who's going?</button>
        `;
        timetable.appendChild(showElement);
    });

    initializeEventHandlers();
}

function initializeEventHandlers() {
    const whosGoingButtons = document.querySelectorAll('.whos-going');

    whosGoingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const showId = button.parentElement.getAttribute('data-show-id');
            fetch(`/show/api/show?id=${showId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                        return;
                    }
                    displayAttendeesModal(data.attendees);
                })
                .catch(error => console.error('Error fetching show attendees:', error));
        });
    });
}

function displayAttendeesModal(attendees) {
    const modal = document.createElement('div');
    modal.classList.add('modal');
    
    const modalContent = document.createElement('div');
    modalContent.classList.add('modal-content');
    
    const closeBtn = document.createElement('span');
    closeBtn.classList.add('close');
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', () => document.body.removeChild(modal));
    
    const attendeesList = document.createElement('div');
    attendeesList.classList.add('attendees-list');

    attendees.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.classList.add('attendee');
        userDiv.innerHTML = `
            <img src="${user.avatarUrl}" alt="${user.username}" title="${user.username}" class="attendee-icon">
            <span>${user.username}</span>
        `;
        attendeesList.appendChild(userDiv);
    });

    modalContent.appendChild(closeBtn);
    modalContent.appendChild(attendeesList);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}
