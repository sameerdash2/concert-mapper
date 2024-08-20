import asyncio
from threading import Thread
from flask import Flask, Blueprint
from flask_cors import CORS

# Set up logging before importing other modules
from src.logger import initialize_logger
initialize_logger()

from src import artists
from src.wss import WebSocketServer

# Application factory
def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprint with routes
    app.register_blueprint(main)

    # This convolution is apparently necessary to run the WebSocket server (an async function)
    # from this function, which is synchronous
    def start_async_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        wss = WebSocketServer(loop)
        # Store wss in the app context
        app.wss = wss

        loop.run_until_complete(wss.start_server())
        loop.run_forever()

    thread = Thread(target=start_async_server, daemon=True)
    thread.start()

    app.logger.info("App started")

    return app


# Create a blueprint
main = Blueprint('main', __name__)

# Define routes
@main.route("/api/artists/<path:artist_name>")
def get_artist(artist_name: str):
    return artists.query_artist(artist_name)

@main.route("/api/setlists/<path:artist_mbid>")
def get_setlists(artist_mbid: str):
    return artists.get_artist_setlists(artist_mbid)
