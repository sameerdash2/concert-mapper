# setlist.py
# Define a custom data type to represent a setlist.
# Stores a subset of the data returned by setlist.fm API, keeping only relevant info

class Setlist:
    # raw_setlist: dict containing raw data from setlist.fm API
    def __init__(self, raw_setlist: dict):
        # Essential fields: if any are missing, mark the setlist as invalid.
        try:
            # Store date in YYYY-MM-DD format (ISO 8601), converting from DD-MM-YYYY
            self.event_date = "-".join(raw_setlist["eventDate"].split("-")[::-1])
            self.city_lat = raw_setlist["venue"]["city"]["coords"]["lat"]
            self.city_long = raw_setlist["venue"]["city"]["coords"]["long"]
        except KeyError:
            raise ValueError("Missing essential setlist data")

        # Optional fields: if missing, set to None
        self.venue_name = raw_setlist["venue"].get("name", None)
        self.city_name = raw_setlist["venue"]["city"].get("name", None)
        self.state_name = raw_setlist["venue"]["city"].get("state", None)
        self.country_name = raw_setlist["venue"]["city"].get("country", {}).get("name", None)
        self.setlist_url = raw_setlist.get("url", None)
        # Count songs performed in all sets. Treat 0 count as missing data.
        song_count = sum(len(set["song"]) for set in raw_setlist["sets"]["set"])
        self.songs_performed = song_count if song_count > 0 else None

    # Convert Setlist object to a dictionary cause Flask needs it
    def to_dict(self) -> dict:
        return {
            "eventDate": self.event_date,
            "venueName": self.venue_name,
            "cityName": self.city_name,
            "cityLat": self.city_lat,
            "cityLong": self.city_long,
            "stateName": self.state_name,
            "countryName": self.country_name,
            "setlistUrl": self.setlist_url,
            "songsPerformed": self.songs_performed
        }
