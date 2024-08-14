import {store, setMessage, updateArtist} from '@/store/state';
import type MapComponent from '@/components/Map.vue';

const isProd = import.meta.env.PROD;

// Defining this type just to make the JSDoc work..
type MapRef = InstanceType<typeof MapComponent> | null;

/**
 * Class for managing the WebSocket connection
 */
export class WebSocketManager {
  private static socket: WebSocket;

  /**
   * Open a new WebSocket connection to the backend server.
   * @param {string} mbid - socket channel, which is an artist MBID
   * @param {MapRef} mapRef - ref to Map component
   */
  static createWebSocket(mbid: string, mapRef: MapRef) {
    const baseUrl = isProd ?
      import.meta.env.VITE_WEBSOCKET_BASE_URL_PROD :
      'ws://localhost:5001';

    this.socket = new WebSocket(`${baseUrl}?mbid=${mbid}`);

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
          // Weed out invalid setlists
          const setlists = data.setlists.filter(
              (setlist: {isValid: boolean}) => setlist.isValid === true
          );
          // Plot new setlists
          mapRef?.plotSetlists(setlists);

          // Display any new information on artist profile
          if (data.totalExpected) {
            updateArtist({concertCount: data.totalExpected});
          }
          break;
        }
        case 'goodbye':
          this.socket?.close();

          setMessage('');

          // Scatter markers that are in the same city
          mapRef?.scatterMarkers();

          store.isFetching = false;
          break;
      }
    };
  }
}
