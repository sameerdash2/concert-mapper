# setlistfm_api.py
# Interface for the setlist.fm API. Defines several functions to interact with the API.

import time
import requests
import json
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

API_URL = "https://api.setlist.fm/rest/1.0/"
API_KEY = os.getenv("SETLISTFM_API_KEY")

# Max number of times to attempt an API request before giving up
MAX_ATTEMPTS = 3
# Delay between retries in ms
RETRY_DELAY = 500


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
                logger.warn(f"In search_artist('{artist_name}'): HTTP {response.status_code}: {response.text[:100]}")

        time.sleep(RETRY_DELAY / 1000)

    # If request unsuccessful, raise an exception
    if not success:
        response.raise_for_status()

    return json.loads(response.text)


def get_artist_setlists(artist_mbid: str) -> dict:
    """Get setlists for an artist by their MusicBrainz ID.

    Raises HTTPError if the response code is not 200 or 404.
    """

    url = API_URL + "artist/" + artist_mbid + "/setlists"
    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json"
    }

    attempts = 0
    success = False
    while attempts < MAX_ATTEMPTS:
        response = requests.get(url, headers=headers)
        attempts += 1
        match response.status_code:
            # Rate limited
            case 429:
                logger.info(f"Rate limited in get_artist_setlists('{artist_mbid}'). Waiting {RETRY_DELAY} ms.")
            # Successful request. 404 means no results.
            case 200 | 404:
                success = True
                break
            # Unknown error. Log and retry.
            case _:
                logger.warn(f"In get_artist_setlists('{artist_mbid}'): HTTP {response.status_code}: {response.text}")

        time.sleep(RETRY_DELAY / 1000)
    
    # If request unsuccessful, raise an exception
    if not success:
        response.raise_for_status()

    return json.loads(response.text)
