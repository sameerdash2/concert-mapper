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
MAX_ATTEMPTS = 5
# Rate limit: minimum interval to aim for between requests
# Official rate limit is 2 reqs per second, but they seem to support
# a speedy turnaround for recently searched artists
RATE_LIMIT_MS = 250


class SetlistFmAPI:
    def __init__(self):
        # Time of the last request
        self.last_request_time = 0
        # Lock for making requests
        self.rate_limit_lock = Lock()

        if API_KEY is None or len(API_KEY) == 0:
            logger.warning("SETLISTFM_API_KEY has not been set")


    def _wait_for_rate_limit(self) -> None:
        """Utility function that returns after a certain amount of time
        has passed since the last request."""
        with self.rate_limit_lock:
            # Store times in milliseconds (python seems to hate this)
            current_time = time.time_ns() // 1_000_000
            elapsed_time = current_time - self.last_request_time

            if elapsed_time < RATE_LIMIT_MS:
                time.sleep((RATE_LIMIT_MS - elapsed_time) / 1000)
            self.last_request_time = time.time_ns() // 1_000_000


    def _perform_request(self, path: str, params: dict, log_info: str) -> dict:
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
        response = None

        for attempts in range(MAX_ATTEMPTS):
            # Wait to go. This aims to respect setlist.fm rate limit, but won't stop all 429s
            self._wait_for_rate_limit()

            # Request
            try:
                response = requests.get(endpoint, params=params, headers=headers, timeout=15)
            except requests.exceptions.ReadTimeout:
                logger.warning(f"Request timed out in {path} for '{log_info}'.")
                continue
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed in {path} for '{log_info}': {e}")
                continue

            # Handle success. 404 means no results.
            if response.status_code == 200 or response.status_code == 404:
                return json.loads(response.text)

            # Begin error land.
            # Exponential backoff, capped at 15 seconds
            delay = min((2 ** attempts) * RATE_LIMIT_MS, 15000)
            match response.status_code:
                # Rate limited
                case 429:
                    logger.info(f"Rate limited in {path} for '{log_info}'. Waiting {delay} ms.")
                # Unknown error.
                case _:
                    # Sometimes they send back HTML for some reason
                    clean_response = "[HTML page]" if '<html' in response.text else response.text.rstrip()
                    logger.warning(f"Error in {path} for '{log_info}': HTTP {response.status_code}: {clean_response}")

            if attempts < MAX_ATTEMPTS - 1:
                time.sleep(delay / 1000)

        logger.info(f"Exhausted {MAX_ATTEMPTS} attempts in {path} for '{log_info}'.")
        if response:
            response.raise_for_status()
        else:
            raise requests.HTTPError


    def search_artist(self, artist_name: str) -> dict:
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

        return self._perform_request(path, params, artist_name)


    def get_artist_setlists(self, artist_mbid: str, page: int) -> dict:
        """Get setlists for an artist by their MusicBrainz ID.

        Raises HTTPError: if the response code is not 200 or 404.
        """

        url = f"/artist/{artist_mbid}/setlists"
        params = {
            "p": page
        }

        return self._perform_request(url, params, f"page {page}")


    def get_artist_info(self, mbid: str) -> dict:
        """Get an artist info by MBID.

        Raises HTTPError if the response code is not 200 or 404.
        """

        path = f"/artist/{mbid}"

        return self._perform_request(path, {}, "")
