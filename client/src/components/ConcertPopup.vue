<!-- Component for the popup of a concert, using the given setlist. -->

<script setup lang="ts">
import type {Setlist} from '@/store/state';
import {formatDate} from '@/services/util';
import {useI18n} from 'vue-i18n';
const {t} = useI18n();

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
    <b>{{ t('table.venue') }}</b>: {{ props.setlist.venueName || 'N/A' }}
  </div>
  <div>
    <b>{{ t('table.songs') }}</b>: {{ props.setlist.songsPerformed || 'N/A' }}
  </div>
  <div>
    <b><a :href="props.setlist.setlistUrl">{{ t('table.viewSetlist') }}</a></b>
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
