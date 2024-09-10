import {reactive} from 'vue';
import L from 'leaflet';

type ProposedArtist = {
  name: string;
  mbid: string;
  imageUrl: string;
}

type Artist = ProposedArtist & {
  concertCount?: number;
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
  proposedArtist: {} as ProposedArtist,
  artist: {} as Artist,
  isFetching: false,
  setlists: [] as Setlist[]
});

export const setMessage = (message: string) => {
  store.message = message;
};

export const setProposedArtist = (artist: ProposedArtist) => {
  store.proposedArtist = artist;
};

export const clearProposedArtist = () => {
  store.proposedArtist = {} as ProposedArtist;
};

export const setArtist = (artist: Artist) => {
  store.artist = artist;
};

/**
 * Update the current artist with new properties.
 * Useful when data slowly trickles in from websocket messages.
 * @param {Partial<Artist>} newProps - new properties
 */
export const updateArtist = (newProps: Partial<Artist>) => {
  store.artist = {...store.artist, ...newProps};
};
