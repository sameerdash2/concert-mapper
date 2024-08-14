import asyncio
import http
import json
import websockets
import logging
import urllib.parse
from typing import Dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.fetcher import Fetcher

logger = logging.getLogger(__name__)

PORT = 5001

# If no clients have connected for an artist by the time their fetch process ends,
# wait this many seconds for someone (hopefully the user who requested it) to connect,
# then close the channel.
GOODBYE_WAIT = 10

# Disable propagation of websockets logs to the root logger
logging.getLogger("websockets").propagate = False

# Mapping of artist mbids to WebSocket connections.
# Artist mbids may persist even after fetching completes
mbids_to_connections: Dict[str, set[websockets.WebSocketServerProtocol]] = {}

# Mapping of artist mbids to Fetcher instances.
# Used to access fetched setlists for newly connected clients
# Any new connections for mbids not in this dict will be refused.
fetchers: Dict[str, 'Fetcher'] = {}


# Override the WebSocketServerProtocol, to handle query parameters before accepting the connection.
class QueryParamProtocol(websockets.WebSocketServerProtocol):
    async def process_request(self, path, headers):
        query = urllib.parse.urlparse(path).query
        params = urllib.parse.parse_qs(query)

        if "mbid" in params:
            mbid = params["mbid"][0]
        else:
            return http.HTTPStatus.UNAUTHORIZED, [], b"Missing mbid\n"

        if mbid not in fetchers:
            return http.HTTPStatus.UNAUTHORIZED, [], b"Invalid mbid\n"

        # Store the mbid on this protocol instance
        self.mbid = mbid


class WebSocketServer:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        # needed so we can force-close connections in the same event loop
        # that they started in, or something
        self.loop = loop
        pass


    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol):
        # In case the fetch process finished between process_request and now...
        if websocket.mbid not in mbids_to_connections or websocket.mbid not in fetchers:
            await websocket.close()
            return

        # Track the client so we can broadcast updates for this artist
        mbids_to_connections[websocket.mbid].add(websocket)

        fetcher = fetchers[websocket.mbid]

        # Send a hello message to the client (not really necessary, but nice to have)
        event = {
            "type": "hello",
            "artistMbid": fetcher.artist_mbid,
            "totalExpected": fetcher.total_expected_setlists
        }
        await websocket.send(json.dumps(event))

        # Send all currently fetched setlists to the client
        if len(fetcher.fetched_setlists) > 0:
            event = {
                "type": "update",
                "setlists": fetcher.fetched_setlists,
                "offset": 0,
                "totalExpected": fetcher.total_expected_setlists
            }
            await websocket.send(json.dumps(event))

        # Now, the client should receive updates as they are broadcasted by the Fetcher instance.

        # Later when they disconnect, update the set of connections
        await websocket.wait_closed()

        try:
            conn_set = mbids_to_connections[websocket.mbid]
        except KeyError:
            # Already removed by the goodbye broadcast (this client lingered too long)
            pass
        else:
            # Remove client to excuse them from forced cleanup.
            # If i understand Python right, I don't have to worry about conn_set being deleted
            conn_set.remove(websocket)


    async def start_server(self):
        server = await websockets.serve(
            self.handle_connection,
            host="localhost",
            port=PORT,
            create_protocol=QueryParamProtocol
        )
        logger.info(f"WebSocket server started on port {PORT}")

        await server.wait_closed()


    # Broadcast an event to all clients connected to a specific artist's "channel"
    # Returns the number of clients broadcasted to.
    def broadcast_to_channel(self, mbid: str, event: dict):
        if mbid in mbids_to_connections:
            websockets.broadcast(mbids_to_connections[mbid], json.dumps(event))
            return len(mbids_to_connections[mbid])


    # Broadcast a goodbye message to a channel, and close all its connections.
    async def broadcast_goodbye_to_channel(self, mbid: str, total_setlists: int):
        # Part 1: Goodbye message

        # Include actual number of setlists fetched.
        goodbye_event = {
            "type": "goodbye",
            "totalSetlists": total_setlists
        }

        # If there are no clients in this channel, wait for at least one to connect
        # before closing the server. Prevents the server from closing too early
        # if the fetch process concludes before any clients connect.
        elapsed = 0
        while len(mbids_to_connections[mbid]) == 0 and elapsed < GOODBYE_WAIT:
            await asyncio.sleep(0.5)
            elapsed += 0.5

        if len(mbids_to_connections[mbid]) == 0:
            logger.warn(f"No clients connected for artist '{mbid}' :(")

        self.broadcast_to_channel(mbid, goodbye_event)

        # Part 2: Shut down the channel

        # Stop any new connections.
        del fetchers[mbid]

        # For any clients that linger around for more than 1 second after
        # the goodbye message, close them.
        await asyncio.sleep(1)

        for conn in mbids_to_connections[mbid]:
            self.loop.create_task(conn.close())

        del mbids_to_connections[mbid]


    # Add a new artist.
    # I would make `fetcher` const if this were C++
    def add_artist(self, mbid: str, fetcher: 'Fetcher'):
        mbids_to_connections[mbid] = set()
        fetchers[mbid] = fetcher
