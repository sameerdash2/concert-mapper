# fanart_tv_api.py
# Interface for the fanart.tv API. Provides functions to get artist images.

import requests
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

API_URL = "https://webservice.fanart.tv/v3"
API_KEY = os.getenv("FANART_TV_API_KEY")

HAVE_API_KEY = API_KEY is not None and len(API_KEY) > 0

if not HAVE_API_KEY:
    logger.warning("FANART_TV_API_KEY has not been set. The app will work without displaying artist images.")


def get_artist_info(mbid: str) -> dict:
    """Get all the info for an artist. fanart.tv has no specific endpoint for images :(
    Args:
        mbid: artist MBID
    Returns:
        The JSON response as a dictionary
    Raises:
        HTTPError: if artist not found on API, or request fails.
        ValueError: if API key is not set.
    """
    if not HAVE_API_KEY:
        raise ValueError

    params = {
        "api_key": API_KEY,
    }
    endpoint = f"{API_URL}/music/${mbid}"
    success = False

    # Request
    response = requests.get(endpoint, params=params)

    match response.status_code:
        # Successful request
        case 200:
            success = True
        # Not found
        case 404:
            pass
        # Unknown error.
        case _:
            logger.warning(f"Error in getting fanart for '{mbid}': HTTP {response.status_code}: {response.text}")

    if not success:
        response.raise_for_status()

    return json.loads(response.text)
