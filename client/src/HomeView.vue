<script setup lang="ts">
import {ref} from 'vue';
import Sidebar from './components/Sidebar.vue';
import Map from './components/Map.vue';

const mapRef = ref<InstanceType<typeof Map> | null>(null);
</script>

<template>
  <div class="columns is-gapless">
    <div id="sidebar" class="column is-narrow">
      <div class="p-3">
        <Sidebar :mapRef="mapRef" />
      </div>
    </div>
    <div class="column">
      <Map ref="mapRef" />
    </div>
  </div>
</template>
