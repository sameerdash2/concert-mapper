# image_api.py
# Interface to get images of artists from external APIs.

from dotenv import load_dotenv
import base64
import logging
import os
import requests
import time

load_dotenv()

logger = logging.getLogger(__name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
DEFAULT_ARTIST_IMAGE_URL = "https://abs.twimg.com/sticky/default_profile_images/default_profile_200x200.png"
MAX_ATTEMPTS = 3
access_token = None

HAVE_API_KEY = (SPOTIFY_CLIENT_ID is not None and SPOTIFY_CLIENT_SECRET is not None and
                len(SPOTIFY_CLIENT_ID) > 0 and len(SPOTIFY_CLIENT_SECRET) > 0)
if not HAVE_API_KEY:
    logger.warning("Spotify credentials have not been set. The app will work without displaying artist images.")


def _refresh_token() -> bool:
    """Get a new access token from Spotify API.
    Returns:
        A boolean indicating whether a new token was fetched
    """
    global access_token
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    # ugly
    auth_encoded = base64.b64encode(auth_string.encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_encoded}'
        }
    )
    if response.status_code != 200:
        logger.error(f"Error fetching Spotify access_token: {response.status_code}: {response.text}")
        return False
    else:
        access_token = response.json()["access_token"]
        return True


def get_artist_image_url(name: str) -> str:
    """Get a URL to the image of an artist.
    If lookup fails, a placeholder image will be returned.
    Args:
        name: artist name, to be looked up
    Returns:
        An image of the artist
    """
    if not HAVE_API_KEY:
        return DEFAULT_ARTIST_IMAGE_URL

    for attempt in range(MAX_ATTEMPTS):
        response = requests.get(
            "https://api.spotify.com/v1/search",
            params={"q": name, "type": "artist", "limit": 1},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 401:
            # Expired token; get a new one.
            if not _refresh_token():
                return DEFAULT_ARTIST_IMAGE_URL
        elif response.status_code == 429:
            # Wait and retry
            logger.warning(f"Rate limited by Spotify API for artist '{name}'. Retrying in 1 second.")
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(1)
        else:
            break

    response_body = response.json()

    if response.status_code != 200:
        logger.error(f"Error fetching artist image for '{name}': {response.status_code}: {response_body}")
        return DEFAULT_ARTIST_IMAGE_URL
    elif len(response_body["artists"]["items"]) == 0:
        # Haven't actually found a query string that yields 0 results,
        # but handling it anyway
        logger.warning(f"No artists found in Spotify API for '{name}'.")
        return DEFAULT_ARTIST_IMAGE_URL
    else:
        # Assume the first artist is the one we want
        artist = response_body["artists"]["items"][0]
        if len(artist["images"]) == 0:
            logger.warning(f"No images found in Spotify API for existing artist '{name}'.")
            return DEFAULT_ARTIST_IMAGE_URL
        else:
            # Give the smallest image
            return artist["images"][-1]["url"]
