<script setup lang="ts">
import {store} from '../store/state';
import ConcertTable from './ConcertTable.vue';
</script>

<template>
  <img
    :src="store.artist.imageUrl"
    alt="Artist"
    class="artist-image"
  >
  <h3>{{ store.artist.name }}</h3>

  <ConcertTable />
</template>

<style scoped>
.artist-image {
  height: 160px;
}
.content h3 {
  /* Undo Bulma's big margin */
  margin-top: .6666em;
}
</style>
