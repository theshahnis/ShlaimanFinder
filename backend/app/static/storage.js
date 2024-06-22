// Save data to local storage
function saveToLocalStorage(key, data) {
    console.log('Saving to Local Storage:', key, data); 
    localStorage.setItem(key, JSON.stringify(data));
}

// Load data from local storage
function loadFromLocalStorage(key) {
    const data = localStorage.getItem(key);
    console.log('Loading from Local Storage:', key, data);
    return data ? JSON.parse(data) : null;
}

// Compare two objects for equality
function deepEqual(obj1, obj2) {
    return JSON.stringify(obj1) === JSON.stringify(obj2);
}

// Fetch friends' locations and save to local storage
function fetchFriendsLocations() {
    fetch('/location/locations')
        .then(response => response.json())
        .then(data => {
            // Save the fetched data to local storage
            saveToLocalStorage('friends_locations', data.users);
            // Update the UI with the fetched data
            displayFriends(data.users);
        })
        .catch(error => {
            console.error('Error fetching friends locations:', error);
            // Try to load data from local storage if fetch fails
            const cachedData = loadFromLocalStorage('friends_locations');
            if (cachedData) {
                displayFriends(cachedData);
            } else {
                document.getElementById('friends-list').innerHTML = 'Error fetching data and no cached data available.';
            }
        });
}

// Display friends data in the UI
function displayFriends(friends) {
    const friendsList = document.getElementById('friends-list');
    friendsList.innerHTML = '';
    friends.forEach(friend => {
        const friendDiv = document.createElement('div');
        friendDiv.className = 'friend';
        friendDiv.innerHTML = `
            <img src="${friend.profile_image}" alt="${friend.username}'s photo" class="friend-img">
            <p>${friend.username}</p>
            <button onclick="viewLocation(${friend.user_id})">View Location</button>
        `;
        friendsList.appendChild(friendDiv);
    });
}

// View a friend's location
function viewLocation(userId) {
    const cachedData = loadFromLocalStorage('friends_locations');
    const user = cachedData ? cachedData.find(user => user.user_id === userId) : null;

    if (user) {
        const latitude = user.latitude;
        const longitude = user.longitude;
        const googleMapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;
        const appleMapsUrl = `maps://maps.apple.com/?q=${latitude},${longitude}`;
        const universalMapsUrl = `https://maps.apple.com/?q=${latitude},${longitude}`; 
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if (isIOS) {
            window.location.href = universalMapsUrl;
        } else {
            window.open(googleMapsUrl, '_blank');
        }
        document.getElementById('location-details').innerHTML = `
            Latitude: ${latitude}<br>
            Longitude: ${longitude}<br>
            Timestamp: ${user.created_at}
        `;
    } else {
        fetch(`/location/${userId}`)
            .then(response => response.json())
            .then(data => {
                if (data.latitude && data.longitude) {
                    const latitude = data.latitude;
                    const longitude = data.longitude;
                    const googleMapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;
                    const appleMapsUrl = `maps://maps.apple.com/?q=${latitude},${longitude}`;
                    const universalMapsUrl = `https://maps.apple.com/?q=${latitude},${longitude}`; 
                    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
                    if (isIOS) {
                        window.location.href = universalMapsUrl;
                    } else {
                        window.open(googleMapsUrl, '_blank');
                    }
                    document.getElementById('location-details').innerHTML = `
                        Latitude: ${latitude}<br>
                        Longitude: ${longitude}<br>
                        Timestamp: ${data.timestamp}
                    `;
                } else {
                    document.getElementById('location-details').innerHTML = 'No location data found.';
                }
            })
            .catch(error => {
                console.error('Error fetching location:', error);
                document.getElementById('location-details').innerHTML = 'Error fetching location data.';
            });
    }
}

// Fetch shows and save to local storage
function fetchShows() {
    if (!isOnline()) {
        const cachedShows = loadFromLocalStorage('shows');
        const cachedShowsAttendees = loadFromLocalStorage('shows_attendees');
        if (cachedShows && cachedShowsAttendees) {
            showOfflineAlert();
            displayShows(cachedShows, cachedShowsAttendees);
        } else {
            document.getElementById('shows-list').innerHTML = 'Error fetching data and no cached data available.';
        }
        return;
    }

    fetch('/show/api/shows')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }
            // Save the fetched data to local storage
            saveToLocalStorage('shows', data.shows);
            saveToLocalStorage('shows_attendees', data.shows_attendees);
            // Update the UI with the fetched data
            allShows = data.shows;
            allShowsAttendees = data.shows_attendees;
            displayShows(allShows, allShowsAttendees);
        })
        .catch(error => {
            console.error('Error fetching shows:', error);
        });
}

// Display shows data in the UI
function displayShows(shows, showsAttendees) {
    const showsList = document.getElementById('shows-list');
    showsList.innerHTML = '';
    for (const stage in shows) {
        for (const date in shows[stage]) {
            shows[stage][date].forEach(show => {
                const showDiv = document.createElement('div');
                showDiv.className = 'show';
                showDiv.innerHTML = `
                    <h3>${show.name}</h3>
                    <p>Stage: ${show.stage}</p>
                    <p>Start Time: ${show.start_time}</p>
                    <p>End Time: ${show.end_time}</p>
                `;
                showsList.appendChild(showDiv);
            });
        }
    }
}

