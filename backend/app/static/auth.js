function storeTokens(api_token) {
    localStorage.setItem('api_token', api_token);  // Store the token in local storage
}

function getStoredApiToken() {
    return localStorage.getItem('api_token');
}

function clearApiToken() {
    document.cookie = 'api_token=; Max-Age=0; path=/; Secure; HttpOnly';
}


function getStoredApiToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; api_token=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function login(email, password, remember = false) {
    fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, password: password, remember: remember })
    })
    .then(response => {
        if (response.ok) {
            return response.json().then(data => {
                if (data.api_token) {
                    storeApiToken(data.api_token);  // Store the token in a cookie
                    const redirectUrl = data.location || '/profile';  // Use fallback URL if Location header is not present
                    window.location.href = redirectUrl;  // Redirect to profile or home page
                } else {
                    alert(data.msg);  // Handle login error
                }
            });
        } else {
            throw new Error('Login failed');
        }
    })
    .catch(error => console.error('Error:', error));
}

function authenticatedFetch(url, options = {}) {
    const token = getStoredApiToken();
    if (!token) {
        window.location.href = '/auth';  // Redirect to login if no token
        return;
    }

    options.headers = {
        ...options.headers,
        'Authorization': 'Bearer ' + token
    };

    return fetch(url, options)
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/auth';  // Redirect to login if unauthorized
                return;
            }
            return response;
        })
        .catch(error => console.error('Error:', error));
}

function logout() {
    clearApiToken();
    window.location.href = '/auth';  // Redirect to login
}