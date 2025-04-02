<script setup lang="ts">
import {ref} from 'vue';
import Sidebar from './components/Sidebar.vue';
import Map from './components/Map.vue';

const mapRef = ref<InstanceType<typeof Map> | null>(null);
</script>

<template>
  <div class="columns is-gapless">
    <div
      id="sidebar"
      class="column is-narrow"
    >
      <div class="p-3">
        <Sidebar :map-ref="mapRef" />
      </div>
    </div>
    <div class="column">
      <Map ref="mapRef" />
    </div>
  </div>
</template>

<style scoped>
#sidebar {
  /* why is this the way to fix the height */
  overflow-x: hidden;
  height: 100vh;
}
/* match the desktop cutoff point for Bulma is-narrow */
@media print, screen and (min-width: 769px) {
  .is-narrow {
    width: 448px;
    max-width: 448px;
  }
}
</style>
