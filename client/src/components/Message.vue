<script setup lang="ts">
import {store} from '../store/state';
</script>

<template>
  <div
    v-if="store.message"
    class="has-text-centered"
  >
    {{ store.message }}
  </div>
  <div v-else>
    &nbsp;
  </div>
</template>
