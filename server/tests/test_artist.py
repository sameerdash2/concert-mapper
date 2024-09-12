def test_invalid_url(client):
    response = client.get("/api/nonsense")
    assert response.status_code == 404
