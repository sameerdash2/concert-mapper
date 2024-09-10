<!-- Component for the popup of a concert, using the given setlist. -->

<script setup lang="ts">
import type {Setlist} from '@/store/state';

const props = defineProps<{
  setlist: Setlist;
}>();

// Interpret date string "YYYY-MM-DD" as a date in local time zone
const [yyyy, mm, dd] = props.setlist.eventDate.split('-').map(Number);
const eventDateString = new Date(yyyy, mm - 1, dd).toLocaleDateString();
</script>

<template>
  <div>
    <b>{{ eventDateString }}</b>
  </div>
  <div>
    <b>{{ props.setlist.cityName }}, {{ props.setlist.countryName }}</b>
  </div>
  <div>
    <b>Venue</b>: {{ props.setlist.venueName || 'N/A' }}
  </div>
  <div>
    <b>Songs</b>: {{ props.setlist.songsPerformed || 'N/A' }}
  </div>
  <div>
    <b><a :href="props.setlist.setlistUrl">View setlist</a></b>
  </div>
</template>

<style scoped>
div:not(:first-child) {
  margin-top: 0.25rem;
}
</style>

<style>
.leaflet-popup-close-button > span {
  font-size: 20px;
}
</style>
