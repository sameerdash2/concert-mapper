import json
import requests_mock
from pathlib import Path
from websockets.sync.client import connect

MXTMOON_MBID = "ccbced49-2689-46f8-9101-1c265d6f7b8f"
JUPITER_MBID = "904e413a-1327-4418-a96d-114a14a874ff"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


jupiter_setlists = [load_json(f"tests/mocks/GET_setlists_jupiter/p{i}.json") for i in range(1, 3)]
mxmtoon_setlists = [load_json(f"tests/mocks/GET_setlists_mxmtoon/p{i}.json") for i in range(1, 7)]


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
        for i, page in enumerate(jupiter_setlists):
            m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}/setlists?p={i+1}", json=page)

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


def test_update_messages(client):
    expected_setlists = json.loads(Path("tests/output/setlists_jupiter.json").read_text(encoding="utf-8"))
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API responses
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}", json={"name": "Boys Go To Jupiter"})
        for i, page in enumerate(jupiter_setlists):
            m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}/setlists?p={i+1}", json=page)

        response = client.get(f"/api/setlists/{JUPITER_MBID}")

        # Connect to websocket
        ws_url = f"ws://localhost:5001?mbid={response.json['mbid']}"
        with connect(ws_url) as websocket:
            # Receive the hello message
            websocket.recv()

            # Receive update messages and accumulate all setlists
            received_setlists = []
            while True:
                response = websocket.recv()
                event = json.loads(response)

                if event["type"] == "update":
                    received_setlists.extend(event["setlists"])
                else:
                    assert event["type"] == "goodbye"
                    break

        # Expect data in received setlists to match expected setlists.
        assert len(received_setlists) == len(expected_setlists)
        for i, setlist in enumerate(received_setlists):
            assert setlist == expected_setlists[i], f"Setlist #{i} does not match expected"


def test_goodbye_message(client):
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API responses
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}", json={"name": "Boys Go To Jupiter"})
        for i, page in enumerate(jupiter_setlists):
            m.get(f"https://api.setlist.fm/rest/1.0/artist/{JUPITER_MBID}/setlists?p={i+1}", json=page)

        response = client.get(f"/api/setlists/{JUPITER_MBID}")

        # Connect to websocket
        ws_url = f"ws://localhost:5001?mbid={response.json['mbid']}"
        with connect(ws_url) as websocket:
            # Receive the hello message
            websocket.recv()
            # Receive update messages until goodbye message
            while True:
                response = websocket.recv()
                event = json.loads(response)
                if event["type"] == "update":
                    continue

                assert event["type"] == "goodbye"
                assert event["totalSetlists"] == 4
                assert event["hadError"] == False
                break
