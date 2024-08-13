<script setup lang="ts">
import {store} from '@/store/state';
import {onMounted, ref, watch} from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type {Setlist} from '@/store/state';

const map = ref<L.Map | null>(null);
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
  map.value = newMap;
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
    if (map.value) {
      L.marker([setlist.cityLat, setlist.cityLong])
          .bindPopup(`<h4>${eventDateString}</h4>
              <h5>${setlist.cityName}, ${setlist.countryName}</h5>
              <div><b>Venue</b>: ${setlist.venueName || 'N/A'}</div>
          <div><b>Songs performed</b>: ${setlist.songsPerformed || 'N/A'}</div>
              <div><a href="${setlist.setlistUrl}">View setlist</a></div>`)
          .addTo(map.value as L.Map);
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
watch(
    store.setlists,
    // not calling it "newSetlists" because it refers to the same array
    (updatedSetlists) => {
      handleUpdatedSetlists(updatedSetlists);
    }
);

/**
 * Clear all existing markers and data on the map.
 */
const clearMap = () => {
  map.value?.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      map.value?.removeLayer(layer);
    }
  });
  plottedSetlists.clear();
};

defineExpose({
  clearMap
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
