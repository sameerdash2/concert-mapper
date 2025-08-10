<script setup lang="ts">
import {store} from '../store/state';
import {formatDate} from '@/services/util';
import {computed} from 'vue';

// store.setlists is not guaranteed to be in order.
// Keep it in descending order.
const sortedSetlists = computed(() => {
  return [...store.setlists].sort((a, b) =>
    b.eventDate.localeCompare(a.eventDate)
  );
});
</script>

<template>
  <table class="table">
    <colgroup>
      <col style="width: 30%;">
      <col style="width: 30%;">
      <col style="width: 40%;">
    </colgroup>
    <thead>
      <tr>
        <th>Date</th>
        <th>City</th>
        <th>Venue</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="setlist in sortedSetlists"
        :key="setlist.setlistUrl"
      >
        <th>
          <a :href="setlist.setlistUrl">{{ formatDate(setlist.eventDate) }}</a>
        </th>
        <td>{{ setlist.cityName }}</td>
        <td>{{ setlist.venueName }}</td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.table {
  width: 100%;
  font-size: 14px;
}
</style>
