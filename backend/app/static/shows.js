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

    const timeSlots = generateTimeSlots();
    const stages = [...new Set(shows.map(show => show.stage))]; // Get unique stages

    // Create grid columns for each stage
    stages.forEach(stage => {
        const stageColumn = document.createElement('div');
        stageColumn.classList.add('stage-column');
        stageColumn.dataset.stage = stage;

        const stageHeader = document.createElement('div');
        stageHeader.classList.add('stage-header');
        stageHeader.textContent = stage;
        stageColumn.appendChild(stageHeader);

        // Create grid rows for each time slot within each stage column
        timeSlots.forEach(slot => {
            const timeSlot = document.createElement('div');
            timeSlot.classList.add('time-slot');
            timeSlot.dataset.time = slot;
            stageColumn.appendChild(timeSlot);
        });

        timetable.appendChild(stageColumn);
    });

    const currentUserId = parseInt(document.querySelector('meta[name="user-id"]').getAttribute('content'));

    shows.forEach(show => {
        const showElement = createShowElement(show, showsAttendees, currentUserId);
        const stageColumn = document.querySelector(`.stage-column[data-stage="${show.stage}"]`);
        const startSlot = stageColumn.querySelector(`.time-slot[data-time="${getTimeSlot(show.start_time)}"]`);

        if (stageColumn && startSlot) {
            const startIndex = Array.from(stageColumn.children).indexOf(startSlot);
            const durationSlots = calculateDurationSlots(show.start_time, show.end_time);

            showElement.style.gridRow = `${startIndex + 1} / span ${durationSlots}`;
            startSlot.appendChild(showElement);
        }
    });

    initializeEventTimetable();
}

function generateTimeSlots() {
    const slots = [];
    const startTime = new Date();
    startTime.setHours(10, 0, 0, 0); // Start at 10:00
    const endTime = new Date(startTime);
    endTime.setDate(endTime.getDate() + 1); // End the next day at 04:00
    endTime.setHours(4, 0, 0, 0);

    while (startTime <= endTime) {
        slots.push(startTime.toTimeString().slice(0, 5));
        startTime.setMinutes(startTime.getMinutes() + 30); // 30-minute intervals
    }
    return slots;
}

function getTimeSlot(time) {
    const date = new Date(time);
    return date.toTimeString().slice(0, 5);
}

function calculateDurationSlots(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const duration = (end - start) / (30 * 60 * 1000); // Duration in 30-minute slots
    return Math.ceil(duration);
}

function createShowElement(show, showsAttendees, currentUserId) {
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

    const showDate = new Date(show.start_time);
    const endDate = new Date(show.end_time);

    showElement.innerHTML = `
        <span class="show-name">${show.name}</span>
        <span class="show-time">${showDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        <button class="select-show">${buttonText}</button>
        <button class="whos-going">Who's going?</button>
        <div class="attendees"></div>
    `;
    return showElement;
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
                    attendeesDiv.appendChild(img);
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
