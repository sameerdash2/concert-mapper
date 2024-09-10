<script setup lang="ts">
import {onMounted, onUnmounted, watch} from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type {Setlist} from '@/store/state';
import {store} from '@/store/state';

// Fix default marker icon not loading when bundled
// https://github.com/Leaflet/Leaflet/issues/4968#issuecomment-269750768

// _getIconUrl tries to hardcode a fully qualified icon path,
// which won't be transformed by the bundler
delete L.Icon.Default.prototype['_getIconUrl' as keyof L.Icon.Default];

import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';
L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl
});
// End of fix

// my verdict is that I don't need a ref here
let map: L.Map | null = null;

const plottedSetlists = new Set<Setlist>();

onMounted(() => {
  // Draw map
  map = L.map('the-map', {
    center: [39.334, -98.218],
    zoom: 4
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

  // Plot existing setlists
  placeSetlistMarkers(store.setlists as Setlist[]);
});

onUnmounted(() => {
  // Must make the markers lose their allegiance to this map,
  // so they can be added to the new map if re-rendered.
  map?.remove();
  map = null;
});

/**
 * Plot some setlists on the map. Uses the markers that exist in each setlist.
 * @param {Setlist[]} setlists - setlists to plot
 */
const placeSetlistMarkers = (setlists: Setlist[]) => {
  setlists.forEach((setlist) => {
    if (map) {
      setlist.marker.addTo(map);
      plottedSetlists.add(setlist);
    }
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

// Watch for changes in setlists store, and plot new ones.
watch(
    store.setlists as Setlist[],
    // not calling it "newSetlists" because it refers to the same array
    (updatedSetlists: Setlist[]) => {
      // Filter out already-plotted setlists
      const newSetlists = updatedSetlists.filter(
          (setlist) => !plottedSetlists.has(setlist)
      );
      placeSetlistMarkers(newSetlists);
    }
);

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
  font-family: inherit;
}
.leaflet-container {
  font-size: 14px;
}
</style>

<style>
/* Placing this style here because it doesn't get proper priority
if placed in ConcertPopup */
.leaflet-popup-content {
  /* default margin: 13px 24px 13px 20px */
  margin: 12px 16px 12px 16px;
}
</style>
