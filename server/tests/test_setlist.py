import json
import requests_mock
from pathlib import Path
from websockets.sync.client import connect

MXTMOON_MBID = "ccbced49-2689-46f8-9101-1c265d6f7b8f"
JUPITER_MBID = "904e413a-1327-4418-a96d-114a14a874ff"


def test_start_fetch_process(client):
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API responses
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{MXTMOON_MBID}", json={"name": "mxmtoon"})
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{MXTMOON_MBID}/setlists", json={})

        response = client.get(f"/api/setlists/{MXTMOON_MBID}")

        assert response.status_code == 200
        assert response.json["mbid"] == MXTMOON_MBID
        assert response.json["wssReady"] == True


def test_hello_message(client):
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API responses
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}", json={"name": "Boys Go To Jupiter"})
        mock_data_p1 = json.loads(Path("tests/mocks/GET_setlists_jupiter/p1.json").read_text(encoding="utf-8"))
        mock_data_p2 = json.loads(Path("tests/mocks/GET_setlists_jupiter/p2.json").read_text(encoding="utf-8"))
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}/setlists?p=1", json=mock_data_p1)
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}/setlists?p=2", json=mock_data_p2)

        response = client.get(f"/api/setlists/{JUPITER_MBID}")

        # Connect to websocket
        ws_url = f"ws://localhost:5001?mbid={response.json['mbid']}"
        with connect(ws_url) as websocket:
            # Wait for the hello message
            response = websocket.recv()
            event = json.loads(response)
            # Check
            assert event["type"] == "hello"
            assert event["artistMbid"] == JUPITER_MBID
            assert event["totalExpected"] == 4
