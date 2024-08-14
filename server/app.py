import asyncio
from threading import Thread
from flask import Flask, Blueprint
from flask_cors import CORS
import logging
import sys
from src import artists
from src.wss import WebSocketServer


# Application factory
def create_app():
    # Set up logging
    file_handler = logging.FileHandler("cm.log")
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
        handlers=handlers
    )

    logging.getLogger("werkzeug").setLevel(logging.ERROR)
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
