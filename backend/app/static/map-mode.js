document.addEventListener('DOMContentLoaded', function() {
    const mapModeToggle = document.getElementById('cycleMapModeButton');
    if (mapModeToggle) {
        mapModeToggle.addEventListener('click', function() {
            cycleMapMode();
        });
    }

    const mapDarkModeToggle = document.getElementById('map-dark-mode-toggle');
    if (mapDarkModeToggle) {
        mapDarkModeToggle.addEventListener('click', function() {
            toggleMapDarkMode();
        });
    }

    // Apply map dark mode based on saved preference
    if (localStorage.getItem('mapDarkMode') === 'enabled') {
        applyMapDarkMode();
    } else {
        removeMapDarkMode();
    }
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
