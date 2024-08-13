import {reactive} from 'vue';

interface ProposedArtist {
  name: string;
  mbid: string;
}

// interface Artist extends ProposedArtist {}

export const store = reactive({
  message: '',
  proposedArtist: {} as ProposedArtist
  // artist: {} as Artist
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
