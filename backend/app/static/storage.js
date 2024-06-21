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

// Call fetchFriendsLocations when the page is loaded
document.addEventListener('DOMContentLoaded', () => {
    fetchFriendsLocations();
});
