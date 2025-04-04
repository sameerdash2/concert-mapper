import {reactive} from 'vue';
import L from 'leaflet';

type Artist = {
  name: string;
  mbid: string;
  imageUrl: string;
}

export type BareSetlist = {
  isValid: boolean,
  eventDate: string,
  venueName: string,
  cityName: string,
  cityLat: number,
  cityLong: number,
  stateName: string,
  countryName: string,
  setlistUrl: string,
  songsPerformed: number
};

export type Setlist = BareSetlist & {
  // Attributes for the Map. Store here, so they can exist independently of Map
  marker: L.Marker<any>,
  scatterLat?: number,
  scatterLong?: number,
}

// The store
export const store = reactive({
  message: '',
  proposedArtist: {} as Artist,
  artist: {} as Artist,
  isFetching: false,
  setlists: [] as Setlist[]
});

export const setMessage = (message: string) => {
  store.message = message;
};

export const setProposedArtist = (artist: Artist) => {
  store.proposedArtist = artist;
};

export const clearProposedArtist = () => {
  store.proposedArtist = {} as Artist;
};

export const setArtist = (artist: Artist) => {
  store.artist = artist;
};
