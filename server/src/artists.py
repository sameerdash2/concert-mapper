# artists.py
# Handles the lookup of artists and initiates the streaming of setlists to the client.

import asyncio
import threading
from flask import Response, jsonify
from requests import HTTPError
from src.setlistfm_api import SetlistFmAPI
from src.fetcher import Fetcher
from src import fanart_tv_api
from flask import current_app

DEFAULT_ARTIST_IMAGE_URL = "https://abs.twimg.com/sticky/default_profile_images/default_profile_200x200.png"

setlistfm = SetlistFmAPI()


# Define our own error handler
def create_error_response(msg: str, code: int) -> tuple[Response, int]:
    return jsonify(error=msg), code


def query_artist(name: str):
    """Looks up an artist by name.
    Args:
        name: Artist name
    Returns:
        A dictionary with info for a single artist.
    """
    # Search for artist, get MBID
    try:
        artist_response = setlistfm.search_artist(name)
        # Naively assume the first artist is the one we want
        artist = artist_response["artist"][0]
    except HTTPError:
        # woops
        return create_error_response("Error searching for artist. Please try again", 500)
    except (KeyError, IndexError):
        return create_error_response("Artist not found", 404)

    mbid = artist["mbid"]
    resolved_artist_name = artist["name"]

    # Get artist image
    image_url = _obtain_image_url(mbid)

    return {
        "mbid": mbid,
        "name": resolved_artist_name,
        "imageUrl": image_url
    }


def get_artist_setlists(mbid: str):
    """Initiates the fetching of setlists for an artist.
    Args:
        mbid: Artist MBID
    Returns:
        dict: A dictionary indicating that the websocket channel is ready.
    """
    # First, pull the WebSocketServer out of the app context to pass to Fetcher.
    # This is needed because the Fetcher will run in a thread, and is therefore outside the app context
    wss = current_app.wss

    # Create a Fetcher instance for this artist that will fetch and stream setlists
    fetcher = Fetcher(mbid, wss)

    # Tell fetcher to start the fetch process
    fetcher.start_setlists_fetch()

    # Send back the mbid (so client can connect to the WebSocket)
    return {
        "mbid": mbid,
        "wssReady": True
    }


def _obtain_image_url(mbid: str) -> str:
    """Get an image URL for an artist by fetching and parsing
    the fanart.tv API response.
    Args:
        mbid: Artist MBID
    Returns:
        str: URL of image
    """
    try:
        artist_info = fanart_tv_api.get_artist_info(mbid)
        artist_thumbs = artist_info["artistthumb"]
    except (HTTPError, ValueError, KeyError):
        return DEFAULT_ARTIST_IMAGE_URL

    # `artistthumb` is an array of artist pictures, each with fields: id, url, likes.
    # Find the artistthumb with the maximum "likes" value.
    thumb_with_max_likes = max(artist_thumbs, key=lambda thumb: int(thumb["likes"]))
    # Get its URL
    raw_url = thumb_with_max_likes["url"]

    # Can replace /fanart with /preview in the URL to get a smaller image --
    # 200x200 instead of 1000x1000. However, i opted not to do this because
    # their downsizing algorithm is potato lol

    return raw_url
