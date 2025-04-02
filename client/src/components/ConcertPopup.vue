<!-- Component for the popup of a concert, using the given setlist. -->

<script setup lang="ts">
import type {Setlist} from '@/store/state';
import {formatDate} from '@/services/util';

const props = defineProps<{
  setlist: Setlist;
}>();

const eventDateString = formatDate(props.setlist.eventDate);
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
