<script setup lang="ts">
import {ref} from 'vue';
import Info from './components/Info.vue';
import Map from './components/Map.vue';
import Message from './components/Message.vue';
import SearchBar from './components/SearchBar.vue';
import ArtistProfile from './components/ArtistProfile.vue';
import {store} from './store/state';

const mapRef = ref<InstanceType<typeof Map> | null>(null);
</script>

<template>
  <div class="cell">
    <SearchBar />
    <Message />
  </div>
  <!-- Main app space -- show side by side on desktop, stacked on mobile -->
  <div class="cell">
    <div class="columns">
      <div
        id="info-column"
        class="column is-narrow"
      >
        <!-- yes i made a truth table for this
            proposed exists | artist exists || show Info | show Profile
            0 0  1 0
            0 1  0 1
            1 0  1 0
            1 1  1 1 -->
        <div
          v-if="!store.artist.mbid || store.proposedArtist.mbid"
          class="mb-4"
        >
          <Info :map-ref="mapRef" />
        </div>
        <hr v-if="store.artist.mbid && store.proposedArtist.mbid">
        <ArtistProfile v-if="store.artist.mbid" />
      </div>
      <div class="column">
        <Map ref="mapRef" />
      </div>
    </div>
  </div>
  <div class="cell has-text-right">
    <RouterLink to="/about">
      About
    </RouterLink>
  </div>
</template>

<style scoped>
#info-column {
  width: 300px;
}
</style>
