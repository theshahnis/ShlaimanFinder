// Function to store tokens in localStorage
function storeTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

// Function to get the access token from localStorage
function getAccessToken() {
    return localStorage.getItem('access_token');
}

// Function to get the refresh token from localStorage
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

// Function to clear tokens from localStorage
function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

// Function to handle login
function login(email, password) {
    fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            storeTokens(data.access_token, data.refresh_token);
            window.location.href = '/profile';  // Redirect to profile or another protected page
        } else {
            alert(data.msg);  // Handle login error
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to make authenticated requests
function authenticatedFetch(url, options = {}) {
    const token = getAccessToken();
    if (!token) {
        window.location.href = '/auth';  // Redirect to login if no token
        return;
    }

    options.headers = {
        ...options.headers,
        'Authorization': 'Bearer ' + token
    };
    if (!(options.body instanceof FormData)) {
        options.headers['Content-Type'] = options.headers['Content-Type'] || 'application/json';
    }

    return fetch(url, options)
        .then(response => {
            if (response.status === 401) {
                return refreshAccessToken()
                    .then(newToken => {
                        if (newToken) {
                            options.headers['Authorization'] = 'Bearer ' + newToken;
                            return fetch(url, options);
                        } else {
                            window.location.href = '/auth';  // Redirect to login if refresh fails
                        }
                    });
            }
            return response;
        })
        .catch(error => console.error('Error:', error));
}

// Function to refresh access token
function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        window.location.href = '/auth';  // Redirect to login if no refresh token
        return;
    }

    return fetch('/auth/refresh', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + refreshToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            storeTokens(data.access_token, refreshToken);  // Refresh only the access token
            return data.access_token;
        } else {
            clearTokens();
            window.location.href = '/auth';  // Redirect to login if refresh fails
        }
    })
    .catch(error => {
        console.error('Error:', error);
        clearTokens();
        window.location.href = '/auth';  // Redirect to login if refresh fails
    });
}

// Function to handle logout
function logout() {
    authenticatedFetch('/auth/logout', {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            clearTokens();
            window.location.href = '/auth';  // Redirect to login
        } else {
            console.error('Logout failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}