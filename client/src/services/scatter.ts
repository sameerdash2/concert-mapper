import {store} from '@/store/state';
import type {Setlist} from '@/store/state';
import L from 'leaflet';

/**
 * Scatter setlists for each city into a circle around the city,
 * to avoid overlap. This modifies the markers of store.setlists in place.
 */
export function assignScatteredCoordinates() {
  /*
    Mapping of city coordinates to setlists.
    Used to distribute setlist coordinates around a circle.
    Cities are keyed by a string of the form "latitude,longitude".
    */
  const citySetlists: Record<string, Setlist[]> = {};

  // Assign setlists to cities
  store.setlists.forEach((setlist) => {
    const cityKey = `${setlist.cityLat},${setlist.cityLong}`;
    if (!citySetlists[cityKey]) {
      citySetlists[cityKey] = [];
    }
    // Prepend this setlist, to maintain chronological order
    // Including a type assertion because TS randomly complains.
    citySetlists[cityKey].unshift(setlist as Setlist);
  });

  // Distribute setlists around a circle for each city
  Object.values(citySetlists).forEach((setlists) => {
    const radius = 0.02 * Math.sqrt(setlists.length - 1);
    const angleStep = 2 * Math.PI / setlists.length;

    setlists.forEach((setlist, index) => {
      // Start at the top of the circle, then go clockwise.
      const angle = (Math.PI / 2) + (angleStep * -index);

      // latitude is Y, and longitude is X...
      const newLatLng = L.latLng(
          setlist.cityLat + radius * Math.sin(angle),
          setlist.cityLong + radius * Math.cos(angle)
      );

      // Seal it
      setlist.marker.setLatLng(newLatLng);
    });
  });
}
