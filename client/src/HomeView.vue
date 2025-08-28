<script setup lang="ts">
import {ref, onMounted} from 'vue';
import {store} from './store/state';
import Map from './components/Map.vue';
import Message from './components/Message.vue';
import Sidebar from './components/Sidebar.vue';
import SearchBar from './components/SearchBar.vue';
import TitleText from './components/TitleText.vue';

const mapRef = ref<InstanceType<typeof Map> | null>(null);
const isMobile = ref(window.innerWidth < 769);

onMounted(() => isMobile.value = window.innerWidth < 769);

</script>

<template>
  <!-- Mobile layout -->
  <div v-if="isMobile" class="mobile-root">
    <div class="top-bar p-3">
      <TitleText class="mb-2" />
      <SearchBar />
      <Message />
    </div>
    <div class="main-content">
      <Sidebar v-if="store.showSidebar" :map-ref="mapRef" class="p-3" />
      <Map v-else ref="mapRef" class="mobile-map" />
    </div>

    <button
      class="button toggle-btn"
      @click="store.showSidebar = !store.showSidebar"
    >
      {{ store.showSidebar ? 'View Map 🗺️' : 'View List 📃' }}
    </button>
  </div>

  <!-- Desktop layout -->
  <div v-else class="columns is-gapless">
    <div id="sidebar" class="column is-narrow">
      <div class="p-3">
        <div class="cell">
          <TitleText class="mb-2" />
          <SearchBar />
          <Message />
        </div>
        <Sidebar :map-ref="mapRef" class="mt-4" />
      </div>
    </div>
    <div class="column">
      <Map ref="mapRef" class="desktop-map" />
    </div>
  </div>
</template>

<style scoped>
#sidebar {
  /* why is this the way to fix the height */
  overflow-x: hidden;
  height: 100vh;
}
.desktop-map {
  height: 100vh;
}
/* match the desktop cutoff point for Bulma is-narrow */
@media print, screen and (min-width: 769px) {
  .is-narrow {
    width: 448px;
    max-width: 448px;
  }
}
/* mobile layout styling */
@media (max-width: 768px) {
  .mobile-root {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  .top-bar {
    box-shadow: 0 1px 4px 0px #5552, 0 2px 6px 2px #5552;
    flex: 0 0 auto;
    z-index: 1500;
  }
  .mobile-map {
    height: 100%;
  }
  .main-content {
    flex: 1 1 0;
    min-height: 0;
    overflow: auto;
    display: flex;
    flex-direction: column;
  }
  .toggle-btn {
    position: fixed;
    bottom: 0;
    z-index: 2000;
    bottom: 24px;
    left: 24px;
    width: 130px;
  }
}
</style>
