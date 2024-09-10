import {
  store,
  setMessage,
  updateArtist,
  type Setlist,
  type BareSetlist
} from '@/store/state';
import {assignScatteredCoordinates} from './scatter';
import {createApp} from 'vue';
import ConcertPopup from '@/components/ConcertPopup.vue';
import L from 'leaflet';

const IS_PROD = import.meta.env.PROD;
const BASE_URL = IS_PROD ?
  import.meta.env.VITE_WEBSOCKET_BASE_URL_PROD :
  'ws://localhost:5001';

/**
 * Class for managing the WebSocket connection
 */
export class WebSocketManager {
  private static socket: WebSocket;
  private static count: number;

  /**
   * Setup process: can be called to "reset" socket for new artist
   * @param {string} mbid - mbid of channel
   */
  private static initialize(mbid: string) {
    this.socket = new WebSocket(`${BASE_URL}?mbid=${mbid}`);
    this.count = 0;
  }

  /**
   * Update status message and artist profile with fetch progress.
   * @param {object} eventData - data of an update event received from websocket
   */
  private static updateMessage(eventData: {totalExpected: number}) {
    updateArtist({concertCount: eventData.totalExpected});
    setMessage(
        `Fetched ${this.count} of ${eventData.totalExpected} concerts...`
    );
  }

  /**
   * Open a new WebSocket connection to the backend server,
   * which will fetch setlists and add them to the global store.
   * @param {string} mbid - socket channel, which is an artist MBID
   */
  static createWebSocket(mbid: string) {
    this.initialize(mbid);

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'hello':
          // Total expected is present in hello message iff the backend
          // has already fetched at least one page of setlists
          if (data.totalExpected) {
            updateArtist({concertCount: data.totalExpected});
          }
          break;
        case 'update': {
          // Count all new setlists
          this.count += data.setlists.length;

          // Update messaging and profile
          this.updateMessage(data);

          // Build setlist objects
          const receivedSetlists: BareSetlist[] = data.setlists.filter(
              (setlist: {isValid: boolean}) => setlist.isValid === true
          );
          const newSetlists: Setlist[] = [];

          receivedSetlists.forEach((setlist) => {
            // Create a Leaflet marker to store within each setlist.
            // Compose a marker and mount it to a new div
            const popupDiv = document.createElement('div');
            createApp(ConcertPopup, {setlist}).mount(popupDiv);

            const marker = L.marker([setlist.cityLat, setlist.cityLong])
                .bindPopup(popupDiv);
            newSetlists.push({
              ...setlist,
              marker
            });
          });

          // Add new setlists to store.
          // The currently active Map component must listen and draw new
          // markers. This module can't talk directly to a map ref, because
          // it'll dismount when the user navigates away.
          store.setlists.push(...newSetlists);
          break;
        }
        case 'goodbye':
          this.socket?.close();

          setMessage(`Fetched ${this.count} concerts`);

          // Now that fetching is finished, scatter setlists to prevent overlap
          assignScatteredCoordinates();

          store.isFetching = false;
          break;
      }
    };
  }
}
