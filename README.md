# Concert Mapper

A web app that maps out the locations of concerts by a given artist. View concerts as pins on an interactive map, and click pins to learn more about each concert (date, venue, setlists). The app uses the [setlist.fm API](https://api.setlist.fm/docs/1.0/index.html) to get concert data.

## Developer Setup

**Requirements**: Python 3, Flask, and a [setlist.fm API key](https://api.setlist.fm/docs/1.0/index.html)

1. Clone the repository and enter the directory
1. Create a Python virtual environment: `python -m venv .venv`
1. Install Flask within the virtual environment: `pip install Flask`
1. Install required packages: `pip install -r requirements.txt`
1. Copy `.env.example` to a new file `.env` and fill in your setlist.fm API key
1. Run the app: `flask run`
