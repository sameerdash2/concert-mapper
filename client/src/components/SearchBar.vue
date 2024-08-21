<script setup lang="ts">
import {
  setMessage,
  setProposedArtist,
  clearProposedArtist
} from '../store/state';
import {onMounted, onUnmounted, ref} from 'vue';
import API_BASE_URL from '@/services/apiBaseUrl';

const searchQuery = defineModel({
  type: String,
  default: ''
});

const searchArtist = () => {
  const searchText = searchQuery.value.trim();
  if (searchText.length === 0) {
    return;
  }

  searchQuery.value = '';
  setMessage('Searching...');
  fetch(`${API_BASE_URL}/api/artists/${encodeURIComponent(searchText)}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
          clearProposedArtist();
          return;
        }

        setProposedArtist(data);

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
      autofocus
    >
  </form>
</template>
