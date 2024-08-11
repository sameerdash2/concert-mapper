<script setup lang="ts">
import {store} from '../store/state';
</script>

<template>
  <h5>Search for an artist to get started</h5>
  <p>
    <b>Artist:</b> {{ store.proposedArtist.name }}
  </p>
  <button class="button">
    Confirm
  </button>
</template>
