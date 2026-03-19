<script setup lang="ts">
import {WebSocketManager} from '@/services/websocket';
import {
  store,
  setMessage,
  setArtist,
  clearProposedArtist
} from '../store/state';
import {computed} from 'vue';
import Map from './Map.vue';
import {API_BASE_URL} from '@/services/util';
import {useI18n} from 'vue-i18n';
const {t} = useI18n();

const props = defineProps<{
  mapRef: InstanceType<typeof Map> | null;
}>();

const proposedArtistExists = computed(() => {
  return Object.keys(store.proposedArtist).length > 0;
});

const handleConfirm = () => {
  setMessage(t('working'));
  // Set proposed artist as actual artist
  setArtist(store.proposedArtist);
  clearProposedArtist();

  const encodedMbid = encodeURIComponent(store.artist.mbid);
  // Make request to setlists endpoint to initialize the fetch process
  fetch(`${API_BASE_URL}/api/setlists/${encodedMbid}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setMessage(data.error);
          store.isFetching = false;
          return;
        } else if (data.wssReady === false) {
          setMessage(t('wsError'));
          store.isFetching = false;
          return;
        }

        // Clear any previous markers
        props.mapRef?.clearMap();

        // Join setlist stream
        WebSocketManager.createWebSocket(store.artist.mbid);
        store.isFetching = true;
      });
};
</script>

<template>
  <div v-if="proposedArtistExists">
    <p>
      <b>{{ $t('artist') }}</b>: {{ store.proposedArtist.name }}
    </p>
    <img
      :src="store.proposedArtist.imageUrl"
      alt="Artist"
      class="artist-image"
    >
    <br>
    <button
      class="button"
      @click="handleConfirm"
    >
      {{ $t('confirm') }}
    </button>
  </div>
</template>

<style scoped>
.artist-image {
  height: 160px;
}
</style>
