<script setup lang="ts">
import {
  store
} from '../store/state';
</script>

<template>
  <h3>{{ store.artist.name }}</h3>
  <div>
    <p>
      <b>Concerts</b>: {{ store.artist.concertCount }}
    </p>
  </div>
</template>
