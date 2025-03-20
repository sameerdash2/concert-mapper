<script setup lang="ts">
import {
  store
} from '../store/state';
</script>

<template>
  <img
    :src="store.artist.imageUrl"
    alt="Artist"
    class="artist-image"
  >
  <h3>{{ store.artist.name }}</h3>
  <div>
    <p>
      <b>Concerts</b>: {{ store.artist.concertCount }}
    </p>
  </div>
</template>

<style scoped>
.artist-image {
  width: 128px;
}
.content h3 {
  /* Undo Bulma's big margin */
  margin-top: .6666em;
}
</style>
