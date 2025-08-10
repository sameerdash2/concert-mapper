from websockets.sync.client import connect
from websockets.exceptions import InvalidStatus


def test_no_mbid_param(client):
    # Connect to websocket without mbid param
    ws_url = f"ws://localhost:5001"
    try:
        connect(ws_url)
        assert False
    except InvalidStatus as e:
        assert "HTTP 401" in str(e)


def test_bad_mbid_param(client):
    # Connect to websocket with mbid that isn't being fetched
    ws_url = f"ws://localhost:5001?mbid=ccbced49-2689-46f8-9101-1c265d6f7b8f"
    try:
        connect(ws_url)
        assert False
    except InvalidStatus as e:
        assert "HTTP 401" in str(e)

