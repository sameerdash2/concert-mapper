const NBSP = '\u00A0';

function initializeMap() {
    // Draw map
    const map = L.map('the-map', {
        center: [39.334, -98.218],
        zoom: 4,
    });

    // Add OpenStreetMap tiles
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Add attribution
    map.attributionControl
        .setPrefix(false)
        .addAttribution('Concert data from <a href="https://www.setlist.fm/">setlist.fm</a>');

    return map;
}

// Populate the profile section of the page
// using data received from /api/artists/
function populateProfile(data) {
    document.getElementById('p-artist').textContent = data.artistName;
    document.getElementById('p-count').textContent = data.numSetlists;

    if (data.numSetlists > 0 && data.setlists.length > 0) {
        const firstSetlist = data.setlists[data.setlists.length - 1];
        const lastSetlist = data.setlists[0];

        // Omit stateName if not included
        document.getElementById('p-first-concert').textContent =
            `${firstSetlist.cityName}${firstSetlist.stateName ? ', ' + firstSetlist.stateName : ''}, ${firstSetlist.countryName}`;
        document.getElementById('p-first-concert').href = firstSetlist.setlistUrl;
        document.getElementById('p-first-date').textContent = `(${firstSetlist.eventDate})`;

        document.getElementById('p-last-concert').textContent =
            `${lastSetlist.cityName}${lastSetlist.stateName ? ', ' + lastSetlist.stateName : ''}, ${lastSetlist.countryName}`;
        document.getElementById('p-last-concert').href = lastSetlist.setlistUrl;
        document.getElementById('p-last-date').textContent = `(${lastSetlist.eventDate})`;
    } else {
        document.getElementById('p-first-concert').textContent = 'N/A';
        document.getElementById('p-first-concert').removeAttribute('href');
        document.getElementById('p-first-date').textContent = '';

        document.getElementById('p-last-concert').textContent = 'N/A';
        document.getElementById('p-last-concert').removeAttribute('href');
        document.getElementById('p-last-date').textContent = '';
    }
}

function plotSetlists(map, setlists) {
    // Mapping of city coordinates to setlists. Used to distribute setlists around a circle.
    // Cities are keyed by a string of the form "latitude,longitude".
    const citySetlists = {};

    // Assign setlists to cities
    setlists.forEach(setlist => {
        const cityKey = `${setlist.cityLat},${setlist.cityLong}`;
        if (!citySetlists[cityKey]) {
            citySetlists[cityKey] = [];
        }
        // Prepend setlist reference, to maintain chronological order
        citySetlists[cityKey].unshift(setlist);
    });

    // Distribute setlists around a circle for each city
    Object.values(citySetlists).forEach(citySetlists => {
        // Set radius depending on number of setlists
        const radius = 0.02 * Math.sqrt(citySetlists.length - 1);
        const angleStep = 2 * Math.PI / citySetlists.length;

        citySetlists.forEach((setlist, index) => {
            // Start at the top of the circle, then go clockwise.
            const angle = (Math.PI / 2) + (angleStep * -index);
            // Store new coordinates
            setlist.transformedLong = setlist.cityLong + radius * Math.cos(angle);
            setlist.transformedLat = setlist.cityLat + radius * Math.sin(angle);
        });
    });

    // Plot markers
    setlists.forEach(setlist => {
        // Interpret date string "YYYY-MM-DD" as a date in local time zone
        const [yyyy, mm, dd] = setlist.eventDate.split('-').map(Number);
        const eventDateString = new Date(yyyy, mm - 1, dd).toLocaleDateString();

        // Plot marker
        L.marker([setlist.transformedLat, setlist.transformedLong])
            .bindPopup(`<h4>${eventDateString}</h4>
            <h5>${setlist.cityName}, ${setlist.countryName}</h5>
            <div><b>Venue</b>: ${setlist.venueName || 'N/A'}</div>
            <div><b>Songs performed</b>: ${setlist.songsPerformed || 'N/A'}</div>
            <div><a href="${setlist.setlistUrl}">View setlist</a></div>`)
            .addTo(map);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const map = initializeMap();
    const message = document.getElementById('message');

    // To be cool, focus input box when '/' is pressed
    document.addEventListener('keydown', function (event) {
        if (event.key === '/') {
            const searchArtist = document.getElementById('search-artist');
            if (document.activeElement !== searchArtist) {
                event.preventDefault();
                searchArtist.focus();
            }
        }
    });

    // Listen to search-form form submission, then read search-artist input box and send a request to server
    document.getElementById('search-form').addEventListener('submit', function (event) {
        event.preventDefault();
        const searchText = document.getElementById('search-artist').value.trim();
        if (searchText.length === 0) {
            return;
        }

        message.textContent = 'Working...';
        fetch(`/api/artists/${encodeURIComponent(searchText)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    message.textContent = data.error;
                    return;
                }

                // temp
                // TODO: use received data to connect to appropriate WebSocket
                console.log(data);
                return;

                // Clear previous markers
                map.eachLayer(layer => {
                    if (layer instanceof L.Marker) {
                        map.removeLayer(layer);
                    }
                });

                // Populate profile section
                populateProfile(data);
                document.getElementById('the-placeholder').style.display = 'none';
                document.getElementById('the-profile-col').style.display = 'block';

                // Add new markers
                plotSetlists(map, data.setlists);

                message.textContent = "Showing 20 most recent concerts";
            })
            .catch(error => {
                console.error(error);
            });
    });
});
