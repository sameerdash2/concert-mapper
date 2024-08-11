<script setup lang="ts">
import Info from './components/Info.vue';
import Map from './components/Map.vue';
import SearchBar from './components/SearchBar.vue';
import TitleText from './components/TitleText.vue';
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
      </div>
      <div class="cell">
        <Info />
      </div>
      <div class="cell">
        <Map />
      </div>
    </div>
  </div>
</template>
