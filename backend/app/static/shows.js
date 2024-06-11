document.addEventListener('DOMContentLoaded', function() {
    const dateButtons = document.querySelectorAll('.button');

    dateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const selectedDate = this.getAttribute('data-date');
            loadShowsForDate(selectedDate, this);
        });
    });

    // Load shows for the first date by default and highlight the first button
    const firstButton = document.querySelector('.button[data-date="2024-06-27"]');
    if (firstButton) {
        firstButton.classList.add('selected');
        loadShowsForDate('2024-06-27', firstButton);
    }
});

function loadShowsForDate(date, selectedButton) {
    fetch(`/show/api/shows?date=${date}`)
        .then(response => response.json())
        .then(data => {
            const shows = data.shows;
            const showsAttendees = data.shows_attendees;
            renderShows(shows, showsAttendees);
        });

    // Remove 'selected' class from all buttons
    const dateButtons = document.querySelectorAll('.button');
    dateButtons.forEach(button => button.classList.remove('selected'));

    // Add 'selected' class to the clicked button
    selectedButton.classList.add('selected');
}

function renderShows(shows, showsAttendees) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = '';  // Clear the timetable

    const stages = {};

    shows.forEach(show => {
        const showDate = new Date(show.start_time);
        const endDate = new Date(show.end_time);
        if (showDate.getHours() < 6) {
            showDate.setDate(showDate.getDate() - 1);
        }
        if (endDate.getHours() < 6) {
            endDate.setDate(endDate.getDate() - 1);
        }

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
            <span>${showDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${endDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            <button class="select-show">Attend</button>
            <div class="attendees"></div>
        `;
        stages[show.stage].appendChild(showElement);

        // Populate existing attendees
        const attendeesDiv = showElement.querySelector('.attendees');
        if (showsAttendees[show.id]) {
            showsAttendees[show.id].forEach(user => {
                const img = document.createElement('img');
                img.src = user.avatarUrl;
                img.alt = user.username;
                img.title = user.username;
                img.classList.add('attendee-icon');
                attendeesDiv.appendChild(img);
            });
        }
    });

    initializeEventTimetable();
}


function initializeEventTimetable() {
    const selectButtons = document.querySelectorAll('.select-show');

    selectButtons.forEach(button => {
        const showId = parseInt(button.parentElement.getAttribute('data-show-id'));

        button.addEventListener('click', function() {
            const action = this.textContent === 'Attend' ? 'attend' : 'leave';
            fetch('/show/select-show', {
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