import requests_mock

MXTMOON_MBID = "ccbced49-2689-46f8-9101-1c265d6f7b8f"

def test_start_fetch_process(client):
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API responses
        m.get(f"https://api.setlist.fm/rest/1.0/artist/{MXTMOON_MBID}", json={"name": "mxmtoon"})
        m.get(f"https://api.setlist.fm/rest/1.0/artists/{MXTMOON_MBID}/setlists", json={})

        response = client.get(f"/api/setlists/{MXTMOON_MBID}")

        assert response.status_code == 200
        assert response.json["mbid"] == MXTMOON_MBID
        assert response.json["wssReady"] == True
