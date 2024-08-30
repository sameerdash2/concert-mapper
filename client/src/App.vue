<script setup lang="ts">
import TitleText from './components/TitleText.vue';

</script>

<template>
  <!-- `content` class tells Bulma to respect classic HTML tags -->
  <div class="content container is-max-widescreen p-4 fixed-grid has-1-cols">
    <div class="grid is-gap-2">
      <div class="cell">
        <TitleText />
      </div>
      <RouterView />
    </div>
  </div>
</template>
