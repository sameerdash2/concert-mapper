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

// Populate profile with initial info about artist
function populateProfile({ artistName }) {
    document.getElementById('p-artist').textContent = artistName;
}

// Update profile if new information is available
function updateProfile({ totalExpected, offset, setlists, firstSetlist }) {
    // Don't want null or undefined
    if (typeof totalExpected === 'number') {
        document.getElementById('p-count').textContent = totalExpected;

        if (totalExpected === 0) {
            document.getElementById('p-first-concert').textContent = 'N/A';
            document.getElementById('p-first-concert').removeAttribute('href');
            document.getElementById('p-first-date').textContent = '';

            document.getElementById('p-last-concert').textContent = 'N/A';
            document.getElementById('p-last-concert').removeAttribute('href');
            document.getElementById('p-last-date').textContent = '';
        }
    }

    if (offset === 0 && setlists.length > 0) {
        const lastSetlist = setlists[0];

        // Omit stateName if not included
        document.getElementById('p-last-concert').textContent =
            `${lastSetlist.cityName}${lastSetlist.stateName ? ', ' + lastSetlist.stateName : ''}, ${lastSetlist.countryName}`;
        document.getElementById('p-last-concert').href = lastSetlist.setlistUrl;
        document.getElementById('p-last-date').textContent = `(${lastSetlist.eventDate})`;
    } else if (firstSetlist) {
        document.getElementById('p-first-concert').textContent =
            `${firstSetlist.cityName}${firstSetlist.stateName ? ', ' + firstSetlist.stateName : ''}, ${firstSetlist.countryName}`;
        document.getElementById('p-first-concert').href = firstSetlist.setlistUrl;
        document.getElementById('p-first-date').textContent = `(${firstSetlist.eventDate})`;
    }
}

function plotSetlists(map, setlists) {
    setlists.forEach(setlist => {
        // Interpret date string "YYYY-MM-DD" as a date in local time zone
        const [yyyy, mm, dd] = setlist.eventDate.split('-').map(Number);
        const eventDateString = new Date(yyyy, mm - 1, dd).toLocaleDateString();

        // Plot marker
        L.marker([setlist.cityLat, setlist.cityLong])
            .bindPopup(`<h4>${eventDateString}</h4>
            <h5>${setlist.cityName}, ${setlist.countryName}</h5>
            <div><b>Venue</b>: ${setlist.venueName || 'N/A'}</div>
            <div><b>Songs performed</b>: ${setlist.songsPerformed || 'N/A'}</div>
            <div><a href="${setlist.setlistUrl}">View setlist</a></div>`)
            .addTo(map);
    });
}

// Scatters markers into a circle around their city, to avoid overlap.
// Intended for use after all setlists are plotted
function scatterMarkers(map) {
    // Mapping of city coordinates to markers. Used to distribute markers around a circle.
    // Cities are keyed by a string of the form "latitude,longitude".
    const citySetlists = {};

    // Assign markers to cities
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            const latLng = layer.getLatLng();
            const cityKey = `${latLng.lat},${latLng.lng}`;
            if (!citySetlists[cityKey]) {
                citySetlists[cityKey] = [];
            }
            // Prepend setlist reference, to maintain chronological order
            citySetlists[cityKey].unshift(layer);
        }
    });

    // Distribute markers around a circle for each city
    Object.values(citySetlists).forEach(markers => {
        const radius = 0.02 * Math.sqrt(markers.length - 1);
        const angleStep = 2 * Math.PI / markers.length;

        markers.forEach((marker, index) => {
            // Start at the top of the circle, then go clockwise.
            const angle = (Math.PI / 2) + (angleStep * -index);
            const currentLatLng = marker.getLatLng();

            // latitude is Y, and longitude is X...
            const newLatLng = L.latLng(
                currentLatLng.lat + radius * Math.sin(angle),
                currentLatLng.lng + radius * Math.cos(angle)
            );

            marker.setLatLng(newLatLng);
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const map = initializeMap();
    const message = document.getElementById('message');
    // Encapsulate fetch status in an object so it can be passed around
    const status = {
        isFetching: false,
        totalExpected: null,
    };

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
        // Prevent multiple requests (may handle this better later)
        if (status.isFetching) {
            return;
        }
        status.isFetching = true;

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
                    status.isFetching = false;
                    return;
                }
                else if (data.wssReady === false) {
                    message.textContent = 'Error: WebSocket server is not ready. Please try again later.';
                    status.isFetching = false;
                    return;
                }

                // Clear previous markers
                map.eachLayer(layer => {
                    if (layer instanceof L.Marker) {
                        map.removeLayer(layer);
                    }
                });

                // Join setlist stream
                joinSetlistStream(data.mbid);

                // Populate profile section
                populateProfile({ artistName: data.artistName });
                document.getElementById('the-placeholder').style.display = 'none';
                document.getElementById('the-profile-col').style.display = 'block';

                message.textContent = "Fetching concerts...";
            })
            .catch(error => {
                console.error(error);
            });
    });


    function joinSetlistStream(mbid) {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        // Remove port if exists and use 5001
        const ws = new WebSocket(`${protocol}://${window.location.host.replace(/:\d+$/, '')}:5001?mbid=${mbid}`);

        let firstSetlist = null;

        ws.onmessage = function (event) {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'hello':
                    status.totalExpected = data.totalExpected;
                    break;
                case 'update':
                    // Weed out invalid setlists
                    setlists = data.setlists.filter(setlist => setlist.isValid === true);
                    // Add new markers
                    plotSetlists(map, setlists);
                    // Pass new information to profile
                    updateProfile(data);
                    // Update first setlist, in case this is the last update
                    firstSetlist = data.setlists[data.setlists.length - 1];
                    break;
                case 'goodbye':
                    ws.close();

                    message.textContent = '\u00A0';
                    updateProfile({ firstSetlist });

                    scatterMarkers(map);

                    status.isFetching = false;
                    break;
            }
        };
    }
});