import asyncio
from threading import Thread
from flask import Flask, Blueprint
from flask_cors import CORS
from connexion import ConnexionMiddleware
from a2wsgi import WSGIMiddleware, ASGIMiddleware
from logger import initialize_logger

# Set up logging before importing other modules
initialize_logger()

import artists
from wss import WebSocketServer

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

    # Set up OpenAPI validation: wrap middleware around the inner WSGI app
    # Connexion only speaks ASGI, so need to add 2 more onion layers for that
    asgi_app = WSGIMiddleware(app.wsgi_app)
    connexion_app = ConnexionMiddleware(asgi_app)
    connexion_app.add_api("api/openapi.yaml",
                          strict_validation=True,
                          validate_responses=True)
    new_wsgi_app = ASGIMiddleware(connexion_app)
    app.wsgi_app = new_wsgi_app

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
