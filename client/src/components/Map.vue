<script setup lang="ts">
import {store} from '@/store/state';
import {onMounted, watch} from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type {Setlist} from '@/store/state';

// my verdict is that I don't need a ref here
let map: L.Map | null = null;

const plottedSetlists = new Set<Setlist>();

onMounted(() => {
  // Draw map
  const newMap = L.map('the-map', {
    center: [39.334, -98.218],
    zoom: 4
  });

  // Add OpenStreetMap tiles
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(newMap);

  // Add attribution
  newMap.attributionControl
      .setPrefix(false)
      .addAttribution('Concert data from <a href="https://www.setlist.fm/">setlist.fm</a>');

  // Update ref
  map = newMap;
});

/**
 * Plot some setlists on the map.
 * @param {Setlist[]} setlists - setlists to plot
 */
const plotSetlists = (setlists: Setlist[]) => {
  setlists.forEach((setlist) => {
    // Interpret date string "YYYY-MM-DD" as a date in local time zone
    const [yyyy, mm, dd] = setlist.eventDate.split('-').map(Number);
    const eventDateString = new Date(yyyy, mm - 1, dd).toLocaleDateString();

    // Plot marker
    if (map) {
      L.marker([setlist.cityLat, setlist.cityLong])
          .bindPopup(`<h4>${eventDateString}</h4>
              <h5>${setlist.cityName}, ${setlist.countryName}</h5>
              <div><b>Venue</b>: ${setlist.venueName || 'N/A'}</div>
          <div><b>Songs performed</b>: ${setlist.songsPerformed || 'N/A'}</div>
              <div><a href="${setlist.setlistUrl}">View setlist</a></div>`)
          .addTo(map);
      plottedSetlists.add(setlist);
    }
  });
};

/**
 * Of the given array, only plot setlists that are not already plotted.
 * @param {Setlist[]} updatedSetlists - full array of setlists
 */
const handleUpdatedSetlists = (updatedSetlists: Setlist[]) => {
  const newSetlists = updatedSetlists.filter(
      (setlist) => !plottedSetlists.has(setlist)
  );
  plotSetlists(newSetlists);
};

// Watch for any change in global setlists, so we can plot new ones
// TODO: no more watching, have websocket directl plot setlists
watch(
    store.setlists,
    // not calling it "newSetlists" because it refers to the same array
    (updatedSetlists) => {
      handleUpdatedSetlists(updatedSetlists);
    }
);

/**
 * Scatter existing map markers into a circle around their city,
 * to avoid overlap.
 */
const scatterMarkers = () => {
  /*
    Mapping of city coordinates to markers.
    Used to distribute markers around a circle.
    Cities are keyed by a string of the form "latitude,longitude".
    */
  const citySetlists: Record<string, L.Marker[]> = {};

  // Assign markers to cities
  map?.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      const {lat, lng} = layer.getLatLng();
      const cityKey = `${lat},${lng}`;
      if (!citySetlists[cityKey]) {
        citySetlists[cityKey] = [];
      }
      // Prepend this marker, to maintain chronological order
      citySetlists[cityKey].unshift(layer);
    }
  });

  // Distribute markers around a circle for each city
  Object.values(citySetlists).forEach((markers) => {
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
};

/**
 * Clear all existing markers and data on the map.
 */
const clearMap = () => {
  map?.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      map?.removeLayer(layer);
    }
  });
  plottedSetlists.clear();
};

defineExpose({
  clearMap,
  scatterMarkers
});
</script>

<template>
  <div id="the-map" />
</template>

<style scoped>
#the-map {
  height: 68vh;
}
</style>
