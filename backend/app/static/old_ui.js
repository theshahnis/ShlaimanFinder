document.addEventListener('DOMContentLoaded', function() {
    const mapModeToggle = document.getElementById('cycleMapModeButton');
    if (mapModeToggle) {
        mapModeToggle.addEventListener('click', function() {
            cycleMapMode();
        });
    }

    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            toggleDarkMode();
        });
    }

    const mapDarkModeToggle = document.getElementById('map-dark-mode-toggle');
    if (mapDarkModeToggle) {
        mapDarkModeToggle.addEventListener('click', function() {
            toggleMapDarkMode();
        });
    }

    // Apply general dark mode based on saved preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    // Apply map dark mode based on saved preference
    if (localStorage.getItem('mapDarkMode') === 'enabled') {
        applyMapDarkMode();
    } else {
        removeMapDarkMode();
    }

    // Highlight the current page's navigation button
    const navButtons = document.querySelectorAll('.nav-button');
    const currentPath = window.location.pathname;

    navButtons.forEach(button => {
        const page = button.getAttribute('data-page');
        const url = button.querySelector('a').getAttribute('href');
        if (currentPath === url || currentPath.startsWith(url)) {
            button.classList.add('selected');
        }
    });
});

let mapModes = ['default', 'moderate', 'dark', 'white'];
let currentMapModeIndex = mapModes.indexOf(localStorage.getItem('mapMode')) || 0;

function cycleMapMode() {
    currentMapModeIndex++;
    if (currentMapModeIndex === mapModes.indexOf('default')) {
        currentMapModeIndex++;
    }
    currentMapModeIndex %= mapModes.length;

    const selectedMode = mapModes[currentMapModeIndex];
    localStorage.setItem('mapMode', selectedMode);
    applyMapMode(selectedMode);
    refreshLocations();
}

function applyMapMode(mode) {
    if (map) {
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });

        let tileLayerUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

        if (mode === 'moderate') {
            tileLayerUrl = 'http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png';
            removeMapDarkMode();
        } else if (mode === 'dark') {
            tileLayerUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
        }

        L.tileLayer(tileLayerUrl, {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
}

function toggleDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    if (darkModeStylesheet.disabled) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    darkModeStylesheet.disabled = false;
    localStorage.setItem('darkMode', 'enabled');
}

function disableDarkMode() {
    const darkModeStylesheet = document.getElementById('dark-mode-stylesheet');
    darkModeStylesheet.disabled = true;
    localStorage.setItem('darkMode', 'disabled');
}

function toggleMapDarkMode() {
    if (localStorage.getItem('mapDarkMode') === 'enabled') {
        removeMapDarkMode();
        localStorage.setItem('mapDarkMode', 'disabled');
    } else {
        applyMapDarkMode();
        localStorage.setItem('mapDarkMode', 'enabled');
    }
}

function applyMapDarkMode() {
    if (map) {
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        }).addTo(map);
    }
}

function removeMapDarkMode() {
    if (map) {
        map.eachLayer(function(layer) {
            map.removeLayer(layer);
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
}
