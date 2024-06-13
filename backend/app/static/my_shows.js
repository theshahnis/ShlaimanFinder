document.addEventListener('DOMContentLoaded', function() {
    loadMyShows();
});

function loadMyShows() {
    fetch('/show/user-shows')
        .then(response => response.json())
        .then(data => {
            const showIds = data.show_ids;
            const showsAttendees = data.shows_attendees;
            fetchShowsByIds(showIds, showsAttendees);
        });
}

function fetchShowsByIds(showIds, showsAttendees) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = ''; // Clear the timetable

    showIds.forEach(showId => {
        fetch(`/show/api/shows?id=${showId}`) // Ensure this endpoint exists
            .then(response => response.json())
            .then(data => {
                renderShow(data, showsAttendees[showId]);
            });
    });
}

function renderShow(show, attendees) {
    const timetable = document.querySelector('.timetable');

    const stageName = show.stage;
    let stageDiv = timetable.querySelector(`.stage[data-stage="${stageName}"]`);

    if (!stageDiv) {
        stageDiv = document.createElement('div');
        stageDiv.classList.add('stage');
        stageDiv.setAttribute('data-stage', stageName);
        stageDiv.innerHTML = `<h2>${stageName}</h2>`;
        timetable.appendChild(stageDiv);
    }

    const showElement = document.createElement('div');
    showElement.classList.add('show');
    showElement.setAttribute('data-show-id', show.id);
    const startTime = new Date(show.start_time);
    const endTime = new Date(show.end_time);
    showElement.innerHTML = `
        <span>${show.name}</span>
        <span>${startTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })} - ${endTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</span>
        <button class="select-show">Attend</button>
        <div class="attendees"></div>
    `;
    stageDiv.appendChild(showElement);

    // Populate existing attendees
    const attendeesDiv = showElement.querySelector('.attendees');
    if (attendees) {
        attendees.forEach(user => {
            const img = document.createElement('img');
            img.src = user.avatarUrl;
            img.alt = user.username;
            img.title = user.username;
            img.classList.add('attendee-icon');
            attendeesDiv.appendChild(img);
        });
    }
}

function renderShows(shows, showsAttendees) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = '';  // Clear the timetable

    const stages = {};
    const currentUserId = parseInt(document.querySelector('meta[name="user-id"]').getAttribute('content')); // Assuming you have a meta tag with user ID

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

        let buttonText = 'Attend';
        if (showsAttendees[show.id]) {
            showsAttendees[show.id].forEach(user => {
                if (user.id === currentUserId) {
                    buttonText = 'Leave';
                }
            });
        }

        showElement.innerHTML = `
            <span>${show.name}</span>
            <span>${showDate.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })} - ${endDate.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</span>
            <button class="select-show">${buttonText}</button>
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
