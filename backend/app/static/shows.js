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
            if (data.error) {
                console.error(data.error);
                return;
            }
            const shows = data.shows;
            const showsAttendees = data.shows_attendees;
            renderShows(shows, showsAttendees);
        })
        .catch(error => console.error('Error loading shows:', error));

    // Remove 'selected' class from all buttons
    const dateButtons = document.querySelectorAll('.button');
    dateButtons.forEach(button => button.classList.remove('selected'));

    // Add 'selected' class to the clicked button
    selectedButton.classList.add('selected');
}

function renderShows(shows, showsAttendees) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = '';  // Clear the timetable

    const stages = {
        'Stage 1': document.createElement('div'),
        'Stage 2': document.createElement('div'),
        'Stage 3': document.createElement('div'),
        'Stage 4': document.createElement('div'),
        'Stage 5': document.createElement('div')
    };

    for (const stage in stages) {
        stages[stage].classList.add('stage');
        stages[stage].setAttribute('data-stage', stage);
        stages[stage].innerHTML = `<h2>${stage}</h2>`;
        timetable.appendChild(stages[stage]);
    }

    shows.forEach(show => {
        const showDate = new Date(show.start_time);
        const endDate = new Date(show.end_time);
        if (showDate.getHours() < 6) {
            showDate.setDate(showDate.getDate() - 1);
        }
        if (endDate.getHours() < 6) {
            endDate.setDate(endDate.getDate() - 1);
        }

        const showElement = document.createElement('div');
        showElement.classList.add('show');
        showElement.setAttribute('data-show-id', show.id);
        showElement.innerHTML = `
            <span class="show-name">${show.name}</span>
            <span class="show-time">${showDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${endDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            <span class="show-stage">${show.stage}</span>
            <button class="select-show">Attend</button>
            <button class="whos-going">Who's going?</button>
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
    const whosGoingButtons = document.querySelectorAll('.whos-going');

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
                const attendeesDiv = this.nextElementSibling.nextElementSibling;
                attendeesDiv.innerHTML = '';
                data.attendees.forEach(user => {
                    const img = document.createElement('img');
                    img.src = user.avatarUrl;
                    img.alt = user.username;
                    img.title = user.username;
                    img.classList.add('attendee-icon');
                    attendeesDiv.append.appendChild(img);
                });

                // Update button text
                if (action === 'attend') {
                    this.textContent = 'Leave';
                } else {
                    this.textContent = 'Attend';
                }
            })
            .catch(error => console.error('Error updating show attendance:', error));
        });
    });

    whosGoingButtons.forEach(button => {
        const showId = parseInt(button.parentElement.getAttribute('data-show-id'));

        button.addEventListener('click', function() {
            fetch(`/show/api/show?id=${showId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                        return;
                    }
                    const attendees = data.attendees;
                    showModal(attendees);
                })
                .catch(error => console.error('Error fetching attendees:', error));
        });
    });
}

function showModal(attendees) {
    const modal = document.createElement('div');
    modal.classList.add('modal');

    const modalContent = document.createElement('div');
    modalContent.classList.add('modal-content');

    const closeButton = document.createElement('span');
    closeButton.classList.add('close');
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    modalContent.appendChild(closeButton);

    const attendeesList = document.createElement('div');
    attendeesList.classList.add('attendees-list');

    attendees.forEach(user => {
        const attendeeDiv = document.createElement('div');
        attendeeDiv.classList.add('attendee');

        const img = document.createElement('img');
        img.src = user.avatarUrl;
        img.alt = user.username;
        img.title = user.username;
        img.classList.add('attendee-icon');

        const username = document.createElement('span');
        username.textContent = user.username;

        attendeeDiv.appendChild(img);
        attendeeDiv.appendChild(username);
        attendeesList.appendChild(attendeeDiv);
    });

    modalContent.appendChild(attendeesList);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
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
