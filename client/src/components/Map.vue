<script setup lang="ts">
import {onMounted, ref} from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const map = ref<L.Map | null>(null);

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
 * Clear all existing markers on the map.
 */
const clearMarkers = () => {
  map.value?.eachLayer((layer) => {
    if (layer instanceof L.Marker) {
      map.value?.removeLayer(layer);
    }
  });
};

defineExpose({
  clearMarkers
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
