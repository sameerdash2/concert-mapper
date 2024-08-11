<script setup lang="ts">
import {store, setMessage} from '../store/state';
import {onMounted, onUnmounted, ref} from 'vue';

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

  setMessage('Searching...');
  fetch(`${API_BASE_URL}/api/artists/${encodeURIComponent(searchText)}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
          store.proposedArtist = {};
          return;
        }

        store.proposedArtist = data;

        setMessage('');
      });
};

// To be cool, focus input box when '/' is pressed
const inputRef = ref<HTMLInputElement | null>(null);
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === '/' &&
      inputRef.value &&
      document.activeElement !== inputRef.value) {
    event.preventDefault();
    inputRef.value.focus();
  }
};
onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
</script>

<template>
  <form @submit.prevent="searchArtist">
    <input
      ref="inputRef"
      v-model="searchQuery"
      class="input"
      type="text"
      placeholder="Search artist..."
    >
  </form>
</template>
