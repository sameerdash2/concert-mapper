<script setup lang="ts">
import TitleText from './TitleText.vue';
import SearchBar from './SearchBar.vue';
import Message from './Message.vue';
import Info from './Info.vue';
import ArtistProfile from './ArtistProfile.vue';
import {store} from '../store/state';
import {InstanceType} from '@/types';
import Map from './Map.vue';

const props = defineProps<{
  mapRef: InstanceType<typeof Map> | null;
}>();

</script>
<template>
  <div class="cell">
    <TitleText class="mb-2" />
    <SearchBar />
    <Message />
  </div>
  <div class="mt-4">
    <!-- yes i made a truth table for this
      proposed exists | artist exists || show Info | show Profile
      0 0  1 0
      0 1  0 1
      1 0  1 0
      1 1  1 1 -->
    <div
      v-if="!store.artist.mbid || store.proposedArtist.mbid"
      class="mb-4"
    >
      <Info :map-ref="props.mapRef" />
    </div>
    <hr v-if="store.artist.mbid && store.proposedArtist.mbid">
    <ArtistProfile v-if="store.artist.mbid" />
  </div>
</template>
