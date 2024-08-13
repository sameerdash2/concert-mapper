<script setup lang="ts">
import {ref} from 'vue';
import Info from './components/Info.vue';
import Map from './components/Map.vue';
import Message from './components/Message.vue';
import SearchBar from './components/SearchBar.vue';
import TitleText from './components/TitleText.vue';

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
        <Info :map-ref="mapRef" />
      </div>
      <div class="cell">
        <Map ref="mapRef" />
      </div>
    </div>
  </div>
</template>
