<script setup lang="ts">
import {WebSocketManager} from '@/services/websocket';
import {
  store,
  setMessage,
  setArtist
} from '../store/state';
import {computed} from 'vue';
import Map from './Map.vue';
import API_BASE_URL from '@/services/apiBaseUrl';

const props = defineProps<{
  mapRef: InstanceType<typeof Map> | null;
}>();

const proposedArtistExists = computed(() => {
  return Object.keys(store.proposedArtist).length > 0;
});

const handleConfirm = () => {
  setMessage('Working...');
  // Set proposed artist as actual artist
  setArtist(store.proposedArtist);

  const encodedMbid = encodeURIComponent(store.proposedArtist.mbid);
  // Make request to setlists endpoint to initialize the fetch process
  fetch(`${API_BASE_URL}/api/setlists/${encodedMbid}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
          // TODO: status fetching false
          return;
        } else if (data.wssReady === false) {
          setMessage(
              'Error: WebSocket server is not ready. Please try again later.');
          // TODO: status fetching false
          return;
        }

        // Clear previous markers
        props.mapRef?.clearMap();

        // Join setlist stream
        WebSocketManager.createWebSocket(store.proposedArtist.mbid);

        // TODO: status fetching true,

        setMessage('Fetching concerts...');
      });
};
</script>

<template>
  <h5>Search for an artist to get started</h5>
  <div v-if="proposedArtistExists">
    <p>
      <b>Artist:</b> {{ store.proposedArtist.name }}
    </p>
    <button
      class="button"
      @click="handleConfirm"
    >
      Confirm
    </button>
  </div>
</template>
