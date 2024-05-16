# setlistfm_api.py
# Interface for the setlist.fm API. Defines several functions to interact with the API.

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.setlist.fm/rest/1.0/"
API_KEY = os.getenv("SETLISTFM_API_KEY")


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

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200 and response.status_code != 404:
        print(f"In search_artist('{artist_name}'): HTTP {response.status_code}: {response.text}")
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

    response = requests.get(url, headers=headers)

    if response.status_code != 200 and response.status_code != 404:
        print(f"In get_artist_setlists('{artist_mbid}'): HTTP {response.status_code}: {response.text}")
        response.raise_for_status()

    return json.loads(response.text)
