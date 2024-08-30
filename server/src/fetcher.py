# fetcher.py
# An instance of the Fetcher class handles the lookup and streaming of setlists to the client, for one artist.

from requests import HTTPError
from src.setlist import Setlist
from src import setlistfm_api
from src.wss import WebSocketServer
import logging

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, artist_mbid: str, wss: WebSocketServer):
        # Data about the artist or their setlists
        self.artist_mbid = artist_mbid
        self.fetched_setlists = []

        # Total expected setlists is known only after the first page is fetched.
        # Until then, use None to convey the unknown state.
        self.total_expected_setlists = None

        # Track state of the fetch process
        self.done_fetching = False

        # Store the app's WebSocketServer instance
        self.wss = wss

        # Just for logging
        self.artist_name = None


    def _update_metadata(self, setlists_response: dict) -> None:
        if "total" in setlists_response:
            self.total_expected_setlists = int(setlists_response["total"])
        if "setlist" in setlists_response and len(setlists_response["setlist"]) > 0:
            self.artist_name = setlists_response["setlist"][0]["artist"]["name"]


    def _broadcast_new_setlists(self, new_setlists: list[Setlist], offset: int) -> None:
        event = {
            "type": "update",
            "setlists": new_setlists,
            "offset": offset,
            "totalExpected": self.total_expected_setlists
        }
        self.wss.broadcast_to_channel(self.artist_mbid, event)


    async def start_setlists_fetch(self):
        logger.info(f"Starting setlists fetch for ({self.artist_mbid})")
        # Inform our WebSocketServer about new artist, so it can create a virtual channel
        self.wss.add_artist(self.artist_mbid, self)

        # Loop for fetching setlists.
        page = 1
        while True:
            # Stores current page of setlists
            raw_setlists = []
            setlists_response = None

            try:
                setlists_response = setlistfm_api.get_artist_setlists(self.artist_mbid, page)
                raw_setlists = setlists_response["setlist"]
            except HTTPError:
                logger.error(
                    f"Aborting fetch for ({self.artist_mbid}) with {len(self.fetched_setlists)}"
                    f" of {self.total_expected_setlists} setlists fetched."
                )
                self.done_fetching = True
            except KeyError:
                # No setlists found for artist.
                # Either they have 0 setlists, or this is the empty page following the last page of results
                # Either way, we are done fetching.
                self.done_fetching = True

            # Update metadata based on response
            if setlists_response is not None:
                self._update_metadata(setlists_response)

            # Broadcast a payload of the new setlists to all connected clients
            new_setlists = Setlist.convert_setlists(raw_setlists)
            self._broadcast_new_setlists(new_setlists, len(self.fetched_setlists))

            # Update the fetched setlists
            self.fetched_setlists.extend(new_setlists)

            # Check if we can conclude
            if self.done_fetching:
                count = len(self.fetched_setlists)
                name_clause = f"'{self.artist_name}' " if self.artist_name else ""
                logger.info(f"Retrieved {count} setlists for {name_clause}({self.artist_mbid})")
                # Broadcast the goodbye message, signaling the end of setlists
                await self.wss.broadcast_goodbye_to_channel(self.artist_mbid, count)
                break

            # Increment page for next request
            page += 1
