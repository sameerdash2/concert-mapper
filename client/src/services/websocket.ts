import {store, setMessage, updateArtist} from '@/store/state';

const isProd = import.meta.env.PROD;

/**
 * Class for managing the WebSocket connection
 */
export class WebSocketManager {
  private static socket: WebSocket;

  /**
   * Open a new WebSocket connection to the backend server.
   * @param {string} mbid - socket channel, which is an artist MBID
   */
  static createWebSocket(mbid: string) {
    const baseUrl = isProd ? import.meta.env.VITE_WEBSOCKET_BASE_URL_PROD : 'ws://localhost:5001';

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
          // Update store. Map will listen to this and plot new setlists
          store.setlists.push(...setlists);

          // Display any new information on artist profile
          if (data.totalExpected) {
            updateArtist({concertCount: data.totalExpected});
          }
          break;
        }
        case 'goodbye':
          this.socket?.close();

          setMessage('');

          // TODO: scatter
          // scatterMarkers(map);

          // TODO: update status false
          // status.isFetching = false;
          break;
      }
    };

    this.socket.onclose = () => {
      // TODO: handle
      console.log('WebSocket closed');
    };
  }
}
