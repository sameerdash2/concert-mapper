# setlist.py
# Define a custom data type to represent a setlist.
# Stores a subset of the data returned by setlist.fm API, keeping only relevant info

class Setlist:
    # raw_setlist: dict containing raw data from setlist.fm API
    def __init__(self, raw_setlist: dict):
        self.event_date = raw_setlist["eventDate"]
        self.venue_name = raw_setlist["venue"]["name"]
        self.city_name = raw_setlist["venue"]["city"]["name"]
        self.city_lat = raw_setlist["venue"]["city"]["coords"]["lat"]
        self.city_long = raw_setlist["venue"]["city"]["coords"]["long"]
        # Sometimes they don't give a state
        self.state_name = raw_setlist["venue"]["city"].get("state", "")
        self.country_name = raw_setlist["venue"]["city"]["country"]["name"]
        self.setlist_url = raw_setlist["url"]
        # Count songs performed in all sets
        self.songs_performed = sum(len(set["song"]) for set in raw_setlist["sets"]["set"])
    
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
