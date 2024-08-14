import {reactive} from 'vue';

interface ProposedArtist {
  name: string;
  mbid: string;
}

interface Artist extends ProposedArtist {
  concertCount?: number;
}

// No flag for validity -- all Setlists must be valid.
export interface Setlist {
  eventDate: string,
  venueName: string,
  cityName: string,
  cityLat: number,
  cityLong: number,
  stateName: string,
  countryName: string,
  setlistUrl: string,
  songsPerformed: number
}

// The store
export const store = reactive({
  message: '',
  proposedArtist: {} as ProposedArtist,
  artist: {} as Artist,
  setlists: [] as Setlist[],
  isFetching: false
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
