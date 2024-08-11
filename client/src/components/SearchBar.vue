<script setup lang="ts">
import {setProposedArtist} from '../store/state';
const isProd = import.meta.env.PROD;

const API_BASE_URL = isProd ?
    import.meta.env.VITE_API_BASE_URL_PROD :
    'http://localhost:8000';

const searchQuery = defineModel({
  type: String,
  default: ''
});

const searchArtist = () => {
  const searchText = searchQuery.value.trim();
  if (searchText.length === 0) {
    return;
  }

  // TODO message
  fetch(`${API_BASE_URL}/api/artists/${encodeURIComponent(searchText)}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          // TODO message
          console.error(data.error);
          return;
        }

        setProposedArtist(data.artistName, data.artistId);

        // TODO message clear
      });
};
</script>

<template>
  <form @submit.prevent="searchArtist">
    <input
      v-model="searchQuery"
      class="input"
      type="text"
      placeholder="Search artist..."
    >
  </form>
</template>
