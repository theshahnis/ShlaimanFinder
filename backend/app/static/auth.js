function storeTokens(api_token) {
    localStorage.setItem('api_token', api_token);  // Store the token in local storage
}

function getStoredApiToken() {
    return localStorage.getItem('api_token');
}

function clearApiToken() {
    localStorage.removeItem('api_token');
}

function storeApiToken(api_token) {
    localStorage.setItem('api_token', api_token);
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
                    storeTokens(data.api_token);  // Ensure this function stores the token
                    const redirectUrl = response.headers.get('Location') || '/profile';  // Use fallback URL if Location header is not present
                    console.log(`Redirecting to ${redirectUrl}`);
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
