from flask import Flask, Response, render_template, jsonify
from flask_assets import Environment, Bundle
from requests import HTTPError
from src import setlistfm_api
from src.setlist import Setlist

app = Flask(__name__)
assets = Environment(app)

js = Bundle('main.js', filters='jsmin', output='dist/packed.js')
assets.register('js_all', js)

css = Bundle('style.css', filters='cssmin', output='dist/style.css')
assets.register('css_all', css)


# Override Flask's long error messages
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error="Internal server error"), 500

@app.errorhandler(404)
def not_found_error(e):
    return jsonify(error="Not found"), 404

# Define our own error handler
def create_error_response(msg: str, code: int) -> tuple[Response, int]:
    return jsonify(error=msg), code


# Define routes
@app.route("/")
def index():
    return render_template('index.html')


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
    setlists = [Setlist(raw_setlist).to_dict() for raw_setlist in raw_setlists]

    return {
        "artist": artist["name"],
        "numSetlists": len(setlists),
        "setlists": setlists
    }
