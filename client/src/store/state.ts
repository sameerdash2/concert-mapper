import {reactive} from 'vue';

interface ProposedArtist {
  name: string;
  mbid: string;
}

// interface Artist extends ProposedArtist {}

export const store = reactive({
  proposedArtist: {} as ProposedArtist
  // artist: {} as Artist
});

export const setProposedArtist = (name: string, mbid: string) => {
  store.proposedArtist = {name, mbid};
};
