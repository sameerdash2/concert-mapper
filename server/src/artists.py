# artists.py
# Handles the lookup of artists and initiates the streaming of setlists to the client.

from flask import Response, jsonify
from requests import HTTPError
from setlistfm_api import SetlistFmAPI
from fetcher import Fetcher
from flask import current_app
from image_api import get_artist_image_url

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
    image_url = get_artist_image_url(resolved_artist_name)

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
