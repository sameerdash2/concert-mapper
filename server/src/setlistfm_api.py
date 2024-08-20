# setlistfm_api.py
# Interface for the setlist.fm API. Defines several functions to interact with the API.

import time
import requests
import json
import os
from dotenv import load_dotenv
import logging
from threading import Lock

load_dotenv()

logger = logging.getLogger(__name__)

API_URL = "https://api.setlist.fm/rest/1.0"
API_KEY = os.getenv("SETLISTFM_API_KEY")

# Max number of times to attempt an API request before giving up
MAX_ATTEMPTS = 3
# Rate limit: minimum interval to aim for between requests
# Official rate limit is 2 reqs per second, but they seem to support
# a speedy turnaround for recently searched artists
RATE_LIMIT_MS = 250
# Delay added to retries, before request is put back into "queue".
RETRY_DELAY = 500

# Time of the last request
last_request_time = 0
# Lock for making requests
rate_limit_lock = Lock()


if API_KEY is None or len(API_KEY) == 0:
    logger.warning("SETLISTFM_API_KEY has not been set")


def _wait_for_rate_limit() -> None:
    """Utility function that returns after a certain amount of time
    has passed since the last request."""
    global last_request_time
    with rate_limit_lock:
        # Store times in milliseconds (python seems to hate this)
        current_time = time.time_ns() // 1_000_000
        elapsed_time = current_time - last_request_time

        if elapsed_time < RATE_LIMIT_MS:
            time.sleep((RATE_LIMIT_MS - elapsed_time) / 1000)
        last_request_time = time.time_ns() // 1_000_000


def _perform_request(path: str, params: dict, log_info: str) -> dict:
    """Make an API request, respecting rate limits and trying multiple attempts.
    Args:
        path: Endpoint path, relative to base URL
        params: Query params
        log_info: A string to include in the log msg if an error happens
    Returns:
        The JSON response as a dictionary
    Raises:
        HTTPError: if the response code of the final attempt is not 200 or 404.
    """

    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }
    endpoint = API_URL + path

    attempts = 0
    success = False
    while attempts < MAX_ATTEMPTS:
        # Wait to go. This aims to respect setlist.fm rate limit, but won't stop all 429s
        _wait_for_rate_limit()

        # Request
        response = requests.get(endpoint, params=params, headers=headers)
        attempts += 1

        match response.status_code:
            # Successful request. 404 means no results.
            case 200 | 404:
                success = True
                break
            # Rate limited
            case 429:
                logger.info(f"Rate limited in {path} for '{log_info}'. Waiting {RETRY_DELAY} ms.")
            # Unknown error.
            case _:
                # Sometimes they send back HTML for some reason
                clean_response = "[HTML page]" if '<html' in response.text else response.text.rstrip()
                logger.warning(f"Error in {path} for '{log_info}': HTTP {response.status_code}: {clean_response}")

        time.sleep(RETRY_DELAY / 1000)

    if not success:
        response.raise_for_status()

    return json.loads(response.text)


def search_artist(artist_name: str) -> dict:
    """Search for an artist by name.

    Raises HTTPError if the response code is not 200 or 404.
    """

    path = "/search/artists"
    # so `sort: relevance` just sorts by number of concerts,
    # but that's the best I can do for now
    params = {
        "artistName": artist_name,
        "sort": "relevance"
    }

    return _perform_request(path, params, artist_name)


def get_artist_setlists(artist_mbid: str, page: int) -> dict:
    """Get setlists for an artist by their MusicBrainz ID.

    Raises HTTPError: if the response code is not 200 or 404.
    """

    url = f"/artist/{artist_mbid}/setlists"
    params = {
        "p": page
    }

    return _perform_request(url, params, f"{artist_mbid}, page {page}")
