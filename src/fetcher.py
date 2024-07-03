# fetcher.py
# An instance of the Fetcher class handles the lookup and streaming of setlists to the client, for one artist.

from requests import HTTPError
from src.setlist import Setlist
from src import setlistfm_api
from src.wss import WebSocketServer
import logging

logger = logging.getLogger(__name__)

def convert_setlists(setlists: list[dict]) -> list[dict]:
    converted_setlists = []
    for raw_setlist in setlists:
        setlist = Setlist(raw_setlist)
        converted_setlists.append(setlist.to_dict())
    return converted_setlists


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


    async def start_setlists_fetch(self):
        logger.info(f"Starting setlists fetch for '{self.artist_mbid}'")
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
                    f"Aborting fetch for '{self.artist_mbid}' with {len(self.fetched_setlists)}"
                    f" of {self.total_expected_setlists} setlists fetched."
                )
                self.done_fetching = True
            except KeyError:
                # No setlists found for artist.
                # Either they have 0 setlists, or this is the empty page following the last page of results
                # Either way, we are done fetching.
                self.done_fetching = True

            # Update total expected if exists
            if setlists_response is not None and "total" in setlists_response:
                self.total_expected_setlists = int(setlists_response["total"])

            # Prepare a broadcast payload of the new setlists for all connected clients
            if len(raw_setlists) > 0:
                new_setlists = convert_setlists(raw_setlists)
                old_count = len(self.fetched_setlists)

                event = {
                    "type": "update",
                    "setlists": new_setlists,
                    "offset": old_count,
                    "totalExpected": self.total_expected_setlists
                }

                # Broadcast them
                self.wss.broadcast_to_channel(self.artist_mbid, event)
                logger.info(f"Broadcasted {len(new_setlists)} new setlists to ?? clients.")

                # Update the fetched setlists
                self.fetched_setlists.extend(new_setlists)
            else:
                # Just in case API returned 200 but no setlists
                self.done_fetching = True

            # Check if we can conclude
            if self.done_fetching:
                # Broadcast the goodbye message, signaling the end of setlists
                await self.wss.broadcast_goodbye_to_channel(self.artist_mbid, len(self.fetched_setlists))

                break

            # Increment page for next request
            page += 1
