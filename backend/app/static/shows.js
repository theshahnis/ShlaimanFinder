document.addEventListener('DOMContentLoaded', function() {
    const dateButtons = document.querySelectorAll('.date-button');
    
    dateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const selectedDate = this.getAttribute('data-date');
            loadShowsForDate(selectedDate);
        });
    });

    // Load shows for the first date by default
    loadShowsForDate('2024-06-27');
});

function loadShowsForDate(date) {
    fetch(`/api/shows?date=${date}`)
    .then(response => response.json())
    .then(data => {
        const shows = data.shows;
        renderShows(shows);

        fetch('/user-shows')
        .then(response => response.json())
        .then(data => {
            const userShowIds = data.show_ids;
            const showsAttendees = data.shows_attendees;
            initializeEventTimetable(userShowIds, showsAttendees);
        });
    });
}

function renderShows(shows) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = '';  // Clear the timetable

    const stages = {};

    shows.forEach(show => {
        if (!stages[show.stage]) {
            stages[show.stage] = document.createElement('div');
            stages[show.stage].classList.add('stage');
            stages[show.stage].innerHTML = `<h2>${show.stage}</h2>`;
            timetable.appendChild(stages[show.stage]);
        }

        const showElement = document.createElement('div');
        showElement.classList.add('show');
        showElement.setAttribute('data-show-id', show.id);
        showElement.innerHTML = `
            <span>${show.name}</span>
            <span>${new Date(show.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${new Date(show.end_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            <button class="select-show">Attend</button>
            <div class="attendees"></div>
        `;
        stages[show.stage].appendChild(showElement);
    });
}

function initializeEventTimetable(userShowIds, showsAttendees) {
    const selectButtons = document.querySelectorAll('.select-show');

    selectButtons.forEach(button => {
        const showId = parseInt(button.parentElement.getAttribute('data-show-id'));
        if (userShowIds.includes(showId)) {
            button.textContent = 'Leave';
        } else {
            button.textContent = 'Attend';
        }

        // Populate existing attendees
        if (showsAttendees[showId]) {
            const attendeesDiv = button.nextElementSibling;
            showsAttendees[showId].forEach(user => {
                const img = document.createElement('img');
                img.src = user.avatarUrl;
                img.alt = user.username;
                img.title = user.username;
                img.classList.add('attendee-icon');
                attendeesDiv.appendChild(img);
            });
        }

        button.addEventListener('click', function() {
            const action = this.textContent === 'Attend' ? 'attend' : 'leave';
            fetch('/select-show', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ showId: showId, action: action })
            })
            .then(response => response.json())
            .then(data => {
                // Update attendees list
                const attendeesDiv = this.nextElementSibling;
                attendeesDiv.innerHTML = '';
                data.attendees.forEach(user => {
                    const img = document.createElement('img');
                    img.src = user.avatarUrl;
                    img.alt = user.username;
                    img.title = user.username;
                    img.classList.add('attendee-icon');
                    attendeesDiv.appendChild(img);
                });

                // Update button text
                if (action === 'attend') {
                    this.textContent = 'Leave';
                } else {
                    this.textContent = 'Attend';
                }
            });
        });
    });
}

// Zoom in on user icon and show name
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('attendee-icon')) {
        const modal = document.createElement('div');
        modal.classList.add('modal');
        const img = document.createElement('img');
        img.src = event.target.src;
        img.alt = event.target.alt;
        img.classList.add('modal-content');
        const caption = document.createElement('div');
        caption.classList.add('caption');
        caption.textContent = event.target.alt;
        modal.appendChild(img);
        modal.appendChild(caption);
        document.body.appendChild(modal);

        modal.addEventListener('click', function() {
            document.body.removeChild(modal);
        });
    }
});
