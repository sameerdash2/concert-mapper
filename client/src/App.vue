<script setup lang="ts">
import {ref} from 'vue';
import Info from './components/Info.vue';
import Map from './components/Map.vue';
import Message from './components/Message.vue';
import SearchBar from './components/SearchBar.vue';
import TitleText from './components/TitleText.vue';
import ArtistProfile from './components/ArtistProfile.vue';
import {store} from './store/state';

const mapRef = ref<InstanceType<typeof Map> | null>(null);
</script>

<template>
  <!-- `content` class tells Bulma to respect classic HTML tags -->
  <div class="content container p-4 fixed-grid has-1-cols">
    <div class="grid is-gap-2">
      <div class="cell">
        <TitleText />
      </div>
      <div class="cell">
        <SearchBar />
        <Message />
      </div>
      <div class="cell">
        <!-- yes i made a truth table for this

        proposed exists | artist exists || show Info | show Profile
        0 0  1 0
        0 1  0 1
        1 0  1 0
        1 1  1 1 -->
        <Info
          v-if="!store.artist.mbid || store.proposedArtist.mbid"
          :map-ref="mapRef"
        />
        <ArtistProfile v-if="store.artist.mbid" />
      </div>
      <div class="cell">
        <Map ref="mapRef" />
      </div>
    </div>
  </div>
</template>
