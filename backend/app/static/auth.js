function storeTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

function login(email, password) {
    fetch('/auth2/login', {
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
            window.location.href = '/home';  // Redirect to home or another protected page
        } else {
            alert(data.msg);  // Handle login error
        }
    })
    .catch(error => console.error('Error:', error));
}

function authenticatedFetch(url, options = {}) {
    const token = getAccessToken();
    if (!token) {
        window.location.href = '/auth2';  // Redirect to login if no token
        return;
    }

    options.headers = {
        ...options.headers,
        'Authorization': 'Bearer ' + token
    };

    return fetch(url, options)
        .then(response => {
            if (response.status === 401) {
                return refreshAccessToken()
                    .then(newToken => {
                        if (newToken) {
                            options.headers['Authorization'] = 'Bearer ' + newToken;
                            return fetch(url, options);
                        } else {
                            window.location.href = '/auth2';  // Redirect to login if refresh fails
                        }
                    });
            }
            return response;
        })
        .catch(error => console.error('Error:', error));
}

function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        window.location.href = '/auth2';  // Redirect to login if no refresh token
        return;
    }

    return fetch('/auth2/refresh', {
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
            window.location.href = '/auth2';  // Redirect to login if refresh fails
        }
    })
    .catch(error => {
        console.error('Error:', error);
        clearTokens();
        window.location.href = '/auth2';  // Redirect to login if refresh fails
    });
}

function logout() {
    clearTokens();
    window.location.href = '/auth2';  // Redirect to login
}
