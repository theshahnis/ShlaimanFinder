let allShows = {};
let allShowsAttendees = {};

document.addEventListener('DOMContentLoaded', function() {
    const dateButtons = document.querySelectorAll('.button');

    dateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const selectedDate = this.getAttribute('data-date');
            loadShowsForDate(selectedDate, this);
        });
    });

    // Fetch all shows once on page load
    if (isOnline()) {
        fetchShowsFromAPI();
    } else {
        showOfflineAlert();
        const cachedData = loadFromLocalStorage('shows');
        if (cachedData) {
            processShowsData(cachedData);
        } else {
            document.getElementById('shows-list').innerHTML = 'No internet connection and no cached data available.';
        }
    }
});

function isOnline() {
    return navigator.onLine;
}

function showOfflineAlert() {
    const offlineAlert = document.getElementById('offline-alert');
    offlineAlert.style.display = 'block';
}

function fetchShowsFromAPI() {
    fetch('/show/api/shows')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }
            allShows = data.shows;
            allShowsAttendees = data.shows_attendees;
            saveToLocalStorage('shows', data);

            // Load shows for the first date by default and highlight the first button
            const firstButton = document.querySelector('.button[data-date="2024-06-27"]');
            if (firstButton) {
                firstButton.classList.add('selected');
                loadShowsForDate('2024-06-27', firstButton);
            }
        })
        .catch(error => console.error('Error loading shows:', error));
}

function loadFromLocalStorage(key) {
    const data = localStorage.getItem(key);
    console.log('Loading from Local Storage:', key, data);
    return data ? JSON.parse(data) : null;
}

function saveToLocalStorage(key, data) {
    console.log('Saving to Local Storage:', key, data); 
    localStorage.setItem(key, JSON.stringify(data));
}

function loadShowsForDate(date, selectedButton) {
    // Filter shows by selected date
    const filteredShows = {};
    for (const [stage, dates] of Object.entries(allShows)) {
        filteredShows[stage] = {};
        if (dates[date]) {
            filteredShows[stage][date] = dates[date];
        }
    }

    renderShows(filteredShows, allShowsAttendees);

    // Remove 'selected' class from all buttons
    const dateButtons = document.querySelectorAll('.button');
    dateButtons.forEach(button => button.classList.remove('selected'));

    // Add 'selected' class to the clicked class to the button
    selectedButton.classList.add('selected');
}

function renderShows(shows, showsAttendees) {
    const timetable = document.querySelector('.timetable');
    timetable.innerHTML = '';  // Clear the timetable

    const stages = {
        'Eagle': document.createElement('div'),
        'Vulture': document.createElement('div'),
        'Buzzard': document.createElement('div'),
        'Hawk': document.createElement('div'),
        'Raven': document.createElement('div')
    };

    const stageLogos = {
        'Eagle': 'eagle_logo.png',
        'Vulture': 'vulture_logo.png',
        'Buzzard': 'buzzard_logo.png',
        'Hawk': 'hawk_logo.png',
        'Raven': 'raven.png'  // Add a default logo or leave this out
    };

    for (const stage of Object.keys(stages)) {
        stages[stage].classList.add('stage');
        stages[stage].setAttribute('data-stage', stage);
        stages[stage].innerHTML = `
            <img src="/images/${stageLogos[stage]}" alt="${stage} Logo" class="stage-logo">
            <h2>${stage}</h2>
        `;
        timetable.appendChild(stages[stage]);
    }

    const currentUserId = parseInt(document.querySelector('meta[name="user-id"]').getAttribute('content'));

    for (const [stage, dates] of Object.entries(shows)) {
        for (const [date, shows] of Object.entries(dates)) {
            shows.forEach(show => {
                const showDate = new Date(show.start_time);
                const endDate = new Date(show.end_time);

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
                    <span>${showDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    <button class="select-show">${buttonText}</button>
                    <button class="whos-going">Who's going?</button>
                    <div class="attendees"></div>
                `;
                stages[show.stage].appendChild(showElement);

                // Populate existing attendees
                const attendeesDiv = showElement.querySelector('.attendees');
                if (showsAttendees[show.id]) {
                    const maxVisibleAttendees = 4;
                    showsAttendees[show.id].slice(0, maxVisibleAttendees).forEach(user => {
                        const img = document.createElement('img');
                        img.src = user.avatarUrl;
                        img.alt = user.username;
                        img.title = user.username;
                        img.classList.add('attendee-icon');
                        attendeesDiv.appendChild(img);
                    });
                    if (showsAttendees[show.id].length > maxVisibleAttendees) {
                        const additionalCount = showsAttendees[show.id].length - maxVisibleAttendees;
                        const additionalCountElement = document.createElement('span');
                        additionalCountElement.classList.add('additional-attendees-count');
                        additionalCountElement.textContent = `+${additionalCount}`;
                        attendeesDiv.appendChild(additionalCountElement);
                    }
                }
            });
        }
    }

    initializeEventTimetable();
}

function initializeEventTimetable() {
    const selectButtons = document.querySelectorAll('.select-show');
    const whosGoingButtons = document.querySelectorAll('.whos-going');

    selectButtons.forEach(button => {
        const showId = parseInt(button.parentElement.getAttribute('data-show-id'));

        button.addEventListener('click', function() {
            if (!isOnline()) {
                showOfflineAlert();
                return;
            }

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
            if (!isOnline()) {
                showOfflineAlert();
                return;
            }

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
