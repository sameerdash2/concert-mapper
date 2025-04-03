# image_api.py
# Interface to get images of artists from external APIs.

from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_ARTIST_IMAGE_URL = "https://abs.twimg.com/sticky/default_profile_images/default_profile_200x200.png"


def get_artist_image_url(mbid: str) -> str:
    """Get a URL to the image of an artist.
    Args:
        mbid: artist MBID
    Returns:
        An image of the artist
    Raises:
        HTTPError: if artist not found on API, or request fails.
        ValueError: if API key is not set.
    """
    # TODO: expand this stub
    return DEFAULT_ARTIST_IMAGE_URL
