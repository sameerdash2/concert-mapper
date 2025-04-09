import pytest
import requests_mock
import json
from pathlib import Path


def test_invalid_url(client):
    response = client.get("/api/nonsense")
    assert response.status_code == 404


def test_get_charlie_puth(client):
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


def test_get_mxmtoon(client):
    mock_data = json.loads(Path("tests/mocks/GET_artists_mxmtoon.json").read_text(encoding="utf-8"))
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API response
        m.get("https://api.setlist.fm/rest/1.0/search/artists", json=mock_data)

        # Test
        response = client.get(f"/api/artists/  mxmtoon")

        # Check
        assert response.status_code == 200
        assert response.json["mbid"] == "ccbced49-2689-46f8-9101-1c265d6f7b8f"
        assert response.json["name"] == "mxmtoon"


def test_get_artist_not_found(client):
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API response to throw 404
        m.get("https://api.setlist.fm/rest/1.0/search/artists", status_code=404, json={})

        # Test
        response = client.get(f"/api/artists/squish")

        # Check
        assert response.status_code == 404


@pytest.mark.timer
def test_get_artist_error(client):
    with requests_mock.Mocker() as m:
        # Mock artist images as nonexistent
        m.get("https://api.spotify.com/v1/search", status_code=404, json={})
        # Mock setlist.fm API response to throw HTTPError
        m.get("https://api.setlist.fm/rest/1.0/search/artists", status_code=500, json={})

        # Test
        response = client.get(f"/api/artists/squish")

        # Check
        assert response.status_code == 500
