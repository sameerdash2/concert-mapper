import requests_mock
import json
from pathlib import Path


def test_invalid_url(client):
    response = client.get("/api/nonsense")
    assert response.status_code == 404


def test_get_artists(client):
    mock_data = json.loads(Path("tests/mocks/GET_artists_Charlie_Puth.json").read_text(encoding="utf-8"))
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API response
        m.get("https://api.setlist.fm/rest/1.0/search/artists", json=mock_data)

        # Test
        response = client.get(f"/api/artists/Charlie Puth")

        # Check
        assert response.status_code == 200
        assert response.json["mbid"] == "525f1f1c-03f0-4bc8-8dfd-e7521f87631b"
        assert response.json["name"] == "Charlie Puth"
