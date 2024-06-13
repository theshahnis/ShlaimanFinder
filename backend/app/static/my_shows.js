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
        fetch(`/show/api/shows?id=${showId}`)
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
        <span>${startTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
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
