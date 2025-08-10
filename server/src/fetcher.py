# fetcher.py
# An instance of the Fetcher class handles the lookup and streaming of setlists to the client, for one artist.

import asyncio
from threading import Thread
from requests import HTTPError
from setlist import Setlist
from setlistfm_api import SetlistFmAPI
from wss import WebSocketServer
from database import Database
import datetime
import logging

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, artist_mbid: str, wss: WebSocketServer, db: Database):
        # Data about the artist or their setlists
        self.artist_mbid = artist_mbid
        self.fetched_setlists = []
        self.artist_name = None
        # Total expected setlists is known only after the first page is fetched.
        # Until then, use None to convey the unknown state.
        self.total_expected_setlists = None

        # Track state of the fetch process
        self.done_fetching = False
        self.error = False

        # Store some tools
        self.wss = wss
        self.db = db

        self.setlistfm = SetlistFmAPI()

    def _update_metadata(self, setlists_response: dict) -> None:
        if "total" in setlists_response:
            self.total_expected_setlists = int(setlists_response["total"])

    def _broadcast_new_setlists(self, new_setlists: list[Setlist]) -> None:
        event = {
            "type": "update",
            "setlists": new_setlists,
            "totalExpected": self.total_expected_setlists
        }
        self.wss.broadcast_to_channel(self.artist_mbid, event)

    def __repr__(self) -> str:
        return f"'{self.artist_name}' ({self.artist_mbid})"

    def _obtain_artist_name(self) -> None:
        """Fetch, and store in self, the current artist's name."""
        try:
            response = self.setlistfm.get_artist_info(self.artist_mbid)
            self.artist_name = response["name"]
        except (KeyError, HTTPError):
            self.artist_name = "??"

    async def _fetch_setlists(self, appending: bool) -> None:
        # Loop for fetching setlists.
        if appending:
            last_setlist = self.db.get_last_setlist(self.artist_mbid)
        else:
            last_setlist = None

        page = 1
        while True:
            # Stores current page of setlists
            raw_setlists = []
            setlists_response = None

            try:
                setlists_response = self.setlistfm.get_artist_setlists(self.artist_mbid, page)
                raw_setlists = setlists_response["setlist"]
            except HTTPError:
                logger.error(
                    f"Aborting fetch for {self} with {len(self.fetched_setlists)}"
                    f" of {self.total_expected_setlists} setlists fetched."
                )
                self.error = True
                self.done_fetching = True
            except KeyError:
                # No setlists found for artist.
                # Either they have 0 setlists, or this is the empty page following the last page of results
                # Either way, we are done fetching.
                self.done_fetching = True

            if setlists_response is not None:
                # Update metadata based on response
                self._update_metadata(setlists_response)

            if len(raw_setlists) > 0 and not self.done_fetching:
                # If appending, only keep raw setlists that are newer than last setlist
                if appending and last_setlist is not None:
                    fresh_setlists = []
                    for setlist in raw_setlists:
                        if (
                            # Stop when we encounter the same URL
                            setlist["url"] == last_setlist["setlistUrl"] or
                            # Rare case: in case last_setlist was deleted off setlist.fm, also check by date.
                            Setlist.convert_date_to_ISO(setlist["eventDate"]) < last_setlist["eventDate"]
                        ):
                            self.done_fetching = True
                            break
                        else:
                            fresh_setlists.append(setlist)
                    raw_setlists = fresh_setlists

                # Broadcast a payload of the new setlists to all connected clients
                new_setlists = Setlist.convert_setlists(raw_setlists)
                self._broadcast_new_setlists(new_setlists)

                # Update the fetched setlists
                self.fetched_setlists.extend(new_setlists)

                # Update the fetched setlists in DB
                self.db.insert_setlists(self.artist_mbid, new_setlists)

            # Check if we can conclude
            if self.done_fetching:
                count = len(self.fetched_setlists)
                logger.info(f"Retrieved {count} setlists for {self}")
                # Mark fetching for this artist as complete in DB
                self.db.mark_artist_complete(self.artist_mbid)
                # Broadcast the goodbye message, signaling the end of setlists
                await self.wss.broadcast_goodbye_to_channel(self.artist_mbid, count, self.error)
                break

            # Increment page for next request
            page += 1

    def start_setlists_fetch(self) -> None:
        """Start the setlist fetch process for an artist. Returns once the websocket is ready."""
        self._obtain_artist_name()

        # Check if artist's setlists are already in DB.
        exists, in_progress, last_updated = self.db.check_artist(self.artist_mbid)

        # If artist hasn't been updated in the last 15 seconds, the fetch likely got stuck. Reset it.
        if exists and in_progress and (
            datetime.datetime.now(tz=datetime.timezone.utc) - last_updated > datetime.timedelta(seconds=15)
        ):
            logger.warning(f"Setlists for {self} were found stuck. Restarting fetch.")
            self.db.delete_artist(self.artist_mbid)
            exists = False

        if exists and in_progress:
            # Fetch in progress: client can join the existing channel.
            logger.info(f"Setlists for {self} are already being fetched; skipping new fetch")
        else:
            # Fetch not in progress.
            if exists:
                # Setlists for artist have been fetched.
                # TODO: Need some condition to purge stored setlists and re-fetch them all,
                # in case old concerts are retroactively added to setlist.fm.
                logger.info(f"Setlists for {self} found in database")

                self.db.reinsert_artist(self.artist_mbid)

                # Pull database setlists into memory before starting the fetch.
                self.fetched_setlists.extend(self.db.get_all_setlists(self.artist_mbid))

                # Fetch only new setlists, appending to those already stored.
                thread = Thread(target=lambda: asyncio.run(self._fetch_setlists(appending=True)))
            else:
                # New artist. Start a new fetch process
                logger.info(f"Starting new setlists fetch for {self}")

                # Add artist to database
                self.db.insert_artist(self.artist_mbid, self.artist_name)

                thread = Thread(target=lambda: asyncio.run(self._fetch_setlists(appending=False)))

            # Inform our WebSocketServer about new artist fetch, so it can create a virtual channel
            self.wss.add_artist(self.artist_mbid, self)

            # Run start_setlists_fetch in a separate thread
            thread.start()
