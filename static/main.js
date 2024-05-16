const NBSP = '\u00A0';

function initializeMap() {
    // Draw map
    const map = L.map('the-map', {
        center: [39.334, -98.218],
        zoom: 4,
    });
    map.attributionControl.setPrefix(false);

    // Add OpenStreetMap tiles
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    return map;
}

// Populate the profile section of the page
// using data received from /api/artists/
function populateProfile(data) {
    document.getElementById('p-artist').textContent = data.artist;
    document.getElementById('p-count').textContent = data.numSetlists;

    if (data.numSetlists > 0 && data.setlists.length > 0) {
        const firstSetlist = data.setlists[data.setlists.length - 1];
        const lastSetlist = data.setlists[0];

        // Can't use template literals because jsmin wrecks the whitespace...
        // Omit stateName if not included
        document.getElementById('p-first-concert').textContent =
            firstSetlist.cityName
            + (firstSetlist.stateName ? ', ' + firstSetlist.stateName : '')
            + ', ' + firstSetlist.countryName;
        document.getElementById('p-first-concert').href = firstSetlist.setlistUrl;
        document.getElementById('p-first-date').textContent = `(${firstSetlist.eventDate})`;

        document.getElementById('p-last-concert').textContent =
            lastSetlist.cityName
            + (lastSetlist.stateName ? ', ' + lastSetlist.stateName : '')
            + ', ' + lastSetlist.countryName;
        document.getElementById('p-last-concert').href = lastSetlist.setlistUrl;
        document.getElementById('p-last-date').textContent = `(${lastSetlist.eventDate})`;
    } else {
        document.getElementById('p-first-concert').textContent = 'N/A';
        document.getElementById('p-first-concert').href = '';
        document.getElementById('p-first-date').textContent = '';

        document.getElementById('p-last-concert').textContent = 'N/A';
        document.getElementById('p-last-concert').href = '';
        document.getElementById('p-last-date').textContent = '';
    }
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
                data.setlists.forEach(setlist => {
                    L.marker([setlist.cityLat, setlist.cityLong])
                        .bindPopup(`<h4>${setlist.eventDate}</h4>
                        <div>${setlist.cityName},&nbsp;${setlist.countryName}</div>
                        <div><b>Venue</b>:&nbsp;${setlist.venueName}</div>
                        <div><b>Songs performed</b>:&nbsp;${setlist.songsPerformed}</div>
                        <div><a href="${setlist.setlistUrl}">View setlist</a></div>`)
                        .addTo(map);
                });

                message.textContent = "Showing 20 most recent concerts";
            })
            .catch(error => {
                console.error(error);
            });
    });
});
