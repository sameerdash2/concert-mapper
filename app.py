from flask import Flask, Response, render_template, jsonify
from flask_assets import Environment, Bundle
from requests import HTTPError
from src import setlistfm_api
from src.setlist import Setlist
import logging
import sys

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

# Create Flask app
app = Flask(__name__)
assets = Environment(app)

js = Bundle('main.js', filters='rjsmin', output='dist/packed.js')
assets.register('js_all', js)

css = Bundle('style.css', filters='cssmin', output='dist/style.css')
assets.register('css_all', css)

# Might print twice in development mode
app.logger.info("App started")


# Define our own error handler
def create_error_response(msg: str, code: int) -> tuple[Response, int]:
    return jsonify(error=msg), code


# Define routes
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/api/artists/<path:artist_name>")
def search_artist(artist_name: str):
    # Step 1: Search for artist, get MBID
    try:
        artist_response = setlistfm_api.search_artist(artist_name)
        # Naively assume the first artist is the one we want
        artist = artist_response["artist"][0]
    except HTTPError:
        # woops
        return create_error_response("Error searching for artist. Please try again", 500)
    except (KeyError, IndexError):
        return create_error_response("Artist not found", 404)

    mbid = artist["mbid"]
    resolved_artist_name = artist["name"]

    # Step 2: Get setlists for artist from MBID
    try:
        setlists_response = setlistfm_api.get_artist_setlists(mbid)
        # TODO: This only gets the first page of setlists. Need to offer pagination
        raw_setlists = setlists_response["setlist"]
    except HTTPError:
        return create_error_response("Error getting setlists. Please try again", 500)
    except KeyError:
        # No setlists found for artist.
        # For this app, we won't treat this as an error.
        raw_setlists = []

    # Convert raw setlists to custom Setlist objects, then to dicts
    setlists = []
    for raw_setlist in raw_setlists:
        try:
            setlist = Setlist(raw_setlist)
        except ValueError:
            # Skip invalid setlists
            continue
        setlists.append(setlist.to_dict())

    app.logger.info(f"Found {len(setlists)} setlists for '{resolved_artist_name}'")

    return {
        "artist": resolved_artist_name,
        "numSetlists": len(setlists),
        "setlists": setlists
    }

if __name__ == "__main__":
    app.run(debug=True)
