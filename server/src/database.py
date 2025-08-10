# database.py
# Interface for storing artist setlists in the database and retrieving them.

from pymongo import MongoClient
from pymongo.collection import Collection
from typing import TypedDict
from setlist import Setlist
import datetime
import logging
import os

logger = logging.getLogger(__name__)


class SetlistDocument(TypedDict):
    isValid: bool
    eventDate: str
    venueName: str
    cityName: str
    cityLat: float
    cityLong: float
    stateName: str
    countryName: str
    setlistUrl: str
    songsPerformed: int


class ArtistDocument(TypedDict):
    mbid: str
    name: str
    lastUpdated: datetime.datetime
    inProgress: bool
    setlists: list[SetlistDocument]


class Database:
    def __init__(self):
        # Short timeout for locating server since this is hosted locally
        self._client = MongoClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=200,
            tz_aware=True
        )
        # Force connection attempt
        self._client.server_info()

        # Keep a handle to the database collection
        db = self._client[os.getenv("MONGO_DB_NAME")]
        self._artists: Collection[ArtistDocument] = db["artists"]

    def insert_artist(self, mbid: str, name: str) -> None:
        """Add a new artist to the database."""
        try:
            self._artists.insert_one(ArtistDocument(
                mbid=mbid,
                name=name,
                lastUpdated=datetime.datetime.now(tz=datetime.timezone.utc),
                inProgress=True,
                setlists=[]
            ))
        except Exception as e:
            logger.error(f"Error inserting new artist '{mbid}': {e}")

    def reinsert_artist(self, mbid: str) -> None:
        """Revive an artist's inProgress fetch status."""
        try:
            self._artists.update_one(
                {"mbid": mbid},
                {"$set": {
                    "inProgress": True,
                    "lastUpdated": datetime.datetime.now(tz=datetime.timezone.utc)
                }}
            )
        except Exception as e:
            logger.error(f"Error reinserting artist '{mbid}': {e}")

    def check_artist(self, mbid: str) -> tuple[bool, bool, datetime.datetime]:
        """Check if an artist is already in the database.
        Returns:
            (exists, inProgress, lastUpdated):
            exists is True if the artist exists in the database.
            inProgress is True if their setlists are being fetched.
            lastUpdated is when they were last fetched.
        """
        try:
            artist = self._artists.find_one({"mbid": mbid})
        except Exception as e:
            logger.error(f"Error checking artist '{mbid}': {e}")
            return False, False, None

        if artist is not None:
            return (
                True,
                artist["inProgress"],
                artist["lastUpdated"]
            )

        return False, False, None

    def insert_setlists(self, mbid: str, new_setlists: list[dict]) -> None:
        """Insert new setlists for an artist."""
        try:
            self._artists.update_one(
                {"mbid": mbid},
                {
                    "$set": {"lastUpdated": datetime.datetime.now(tz=datetime.timezone.utc)},
                    "$push": {"setlists": {"$each": new_setlists}}
                }
            )
        except Exception as e:
            logger.error(f"Error inserting new setlists for '{mbid}': {e}")

    def get_all_setlists(self, mbid: str) -> list[Setlist]:
        """Get all setlists stored in the database for an artist."""
        try:
            artist = self._artists.find_one({"mbid": mbid})
        except Exception as e:
            logger.error(f"Error retrieving all setlists for '{mbid}': {e}")
            return []

        # hope the artist was found
        return artist["setlists"] if artist else []

    def get_last_setlist(self, mbid: str) -> Setlist | None:
        """Get the most recent setlist stored for an artist. Returns None if no setlists stored."""
        pipeline = [
            {"$match": {"mbid": mbid}},
            {
                # Write the last setlist into a new field `lastSetlist`
                "$set": {
                    "lastSetlist": {
                        "$arrayElemAt": [
                            # Sort by descending eventDate, then take first elem
                            {"$sortArray": {
                                "input": "$setlists",
                                "sortBy": {"eventDate": -1}
                            }},
                            0
                        ]
                    }
                }
            },
            {"$project": {"_id": 0, "lastSetlist": 1}}
        ]

        try:
            result = list(self._artists.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error retrieving last setlist for '{mbid}': {e}")
            return None
        last_setlist = result[0]["lastSetlist"] if result else None
        return last_setlist

    def mark_artist_complete(self, mbid: str) -> None:
        try:
            self._artists.update_one(
                {"mbid": mbid},
                {"$set": {
                    "inProgress": False,
                    "lastUpdated": datetime.datetime.now(tz=datetime.timezone.utc)
                }}
            )
        except Exception as e:
            logger.error(f"Error marking artist '{mbid}' as complete: {e}")

    def delete_artist(self, mbid: str) -> None:
        try:
            self._artists.delete_one({"mbid": mbid})
        except Exception as e:
            logger.error(f"Error deleting artist '{mbid}': {e}")

    def close(self) -> None:
        self._client.close()
