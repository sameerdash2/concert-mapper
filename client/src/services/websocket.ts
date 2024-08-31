import {store, setMessage, updateArtist} from '@/store/state';
import type MapComponent from '@/components/Map.vue';

const IS_PROD = import.meta.env.PROD;
const BASE_URL = IS_PROD ?
  import.meta.env.VITE_WEBSOCKET_BASE_URL_PROD :
  'ws://localhost:5001';

// Defining this type just to make the JSDoc work..
type MapRef = InstanceType<typeof MapComponent> | null;

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
   * Open a new WebSocket connection to the backend server.
   * @param {string} mbid - socket channel, which is an artist MBID
   * @param {MapRef} mapRef - ref to Map component
   */
  static createWebSocket(mbid: string, mapRef: MapRef) {
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

          // Weed out invalid setlists
          const setlists = data.setlists.filter(
              (setlist: {isValid: boolean}) => setlist.isValid === true
          );
          // Plot new setlists
          mapRef?.plotSetlists(setlists);
          break;
        }
        case 'goodbye':
          this.socket?.close();

          setMessage(`Fetched ${this.count} concerts`);

          // Scatter markers that are in the same city
          mapRef?.scatterMarkers();

          store.isFetching = false;
          break;
      }
    };
  }
}
