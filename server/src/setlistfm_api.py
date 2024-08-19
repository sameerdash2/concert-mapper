# setlistfm_api.py
# Interface for the setlist.fm API. Defines several functions to interact with the API.

import time
import requests
import json
import os
from dotenv import load_dotenv
import logging
from threading import Lock

logger = logging.getLogger(__name__)

load_dotenv()

API_URL = "https://api.setlist.fm/rest/1.0/"
API_KEY = os.getenv("SETLISTFM_API_KEY")

if API_KEY is None or len(API_KEY) == 0:
    logger.warning("SETLISTFM_API_KEY has not been set")

# Max number of times to attempt an API request before giving up
MAX_ATTEMPTS = 3
# Rate limit: minimum interval to aim for between requests
RATE_LIMIT_MS = 500
# Delay added to retries, on top of rate limit gap.
RETRY_DELAY = 500

# Time of the last request
last_request_time = 0
# Lock for making requests
rate_limit_lock = Lock()


def wait_for_rate_limit():
    """Utility function that returns after a certain amount of time
    has passed since the last request."""
    global last_request_time
    with rate_limit_lock:
        current_time = time.time()
        # Convert to milliseconds
        elapsed_time = (current_time - last_request_time) * 1000

        if elapsed_time < RATE_LIMIT_MS:
            time.sleep((RATE_LIMIT_MS - elapsed_time) / 1000)
        last_request_time = time.time()


def search_artist(artist_name: str) -> dict:
    """Search for an artist by name.

    Raises HTTPError if the response code is not 200 or 404.
    """

    url = API_URL + "search/artists"
    params = {
        "artistName": artist_name,
        "sort": "relevance"
    }
    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }

    attempts = 0
    success = False
    while attempts < MAX_ATTEMPTS:
        wait_for_rate_limit()
        response = requests.get(url, params=params, headers=headers)
        attempts += 1

        match response.status_code:
            # Rate limited
            case 429:
                logger.info(f"Rate limited in search_artist('{artist_name}'). Waiting {RETRY_DELAY} ms.")
            # Successful request. 404 means no results.
            case 200 | 404:
                success = True
                break
            # Unknown error. Log and retry.
            case _:
                # Sometimes they send back HTML for some reason
                clean_response = "[HTML page]" if '<html' in response.text else response.text.rstrip()
                logger.warn(f"In search_artist('{artist_name}'): HTTP {response.status_code}: {clean_response}")

        time.sleep(RETRY_DELAY / 1000)

    # If request unsuccessful, raise an exception
    if not success:
        response.raise_for_status()

    return json.loads(response.text)


def get_artist_setlists(artist_mbid: str, page: int) -> dict:
    """Get setlists for an artist by their MusicBrainz ID.

    Raises HTTPError if the response code is not 200 or 404.
    """

    url = API_URL + "artist/" + artist_mbid + "/setlists"
    params = {
        "p": page
    }
    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }

    attempts = 0
    success = False
    while attempts < MAX_ATTEMPTS:
        wait_for_rate_limit()
        response = requests.get(url, params=params, headers=headers)
        attempts += 1
        match response.status_code:
            # Rate limited
            case 429:
                logger.info(f"Rate limited in get_artist_setlists('{artist_mbid}', {page}). Waiting {RETRY_DELAY} ms.")
            # Successful request. 404 means no results.
            case 200 | 404:
                success = True
                break
            # Unknown error. Log and retry.
            case _:
                # Sometimes they send back HTML for some reason
                clean_response = "[HTML page]" if '<html' in response.text else response.text.rstrip()
                logger.warn(f"In get_artist_setlists('{artist_mbid}', {page}):"
                            f" HTTP {response.status_code}: {clean_response}")

        time.sleep(RETRY_DELAY / 1000)

    # If request unsuccessful, raise an exception
    if not success:
        response.raise_for_status()

    return json.loads(response.text)
