<script setup lang="ts">
import {store} from '../store/state';
import {computed} from 'vue';

const proposedArtistExists = computed(() => {
  return Object.keys(store.proposedArtist).length > 0;
});
</script>

<template>
  <h5>Search for an artist to get started</h5>
  <div v-if="proposedArtistExists">
    <p>
      <b>Artist:</b> {{ store.proposedArtist.name }}
    </p>
    <button class="button">
      Confirm
    </button>
  </div>
</template>
