# Address lookup

## Current implementation

`lookup-address` resolves an address through **OpenStreetMap Nominatim**:

```bash
python3 -m pzmapstudio.cli lookup-address \
  --address "улица Ленина 1, Исилькуль" \
  --scene isilkul-region.json \
  --x 120 --y 80 --improvise
```

It returns:

- canonical display name;
- latitude/longitude;
- OSM bounding box;
- building tags (`building:levels`, material, roof shape when present);
- a human-openable Google Maps search URL.

With `--improvise` it makes a first-pass rectangular building from the bounding
box and the tagged floor count. This is a silhouette-level improvisation, not a
photo reconstruction.

## Google Maps boundary

This project does **not** scrape Google Maps or Street View. Their terms do not
allow bulk downloading, caching or redistributing imagery. The tool stores a
Google Maps URL for a human to open, not Google imagery.

If an official Google integration is needed, add an opt-in provider using the
Google Maps Platform APIs and a user-owned API key. Check the current terms for
each API before storing or republishing any returned imagery.

## Photo references

For facade detail, attach a user-supplied screenshot or an openly licensed
photo:

```bash
python3 -m pzmapstudio.cli add-reference \
  --scene isilkul-region.json \
  --building cell-7-68-b12 \
  --title "СКК имени Блинова" \
  --path references/skk.jpg \
  --url "https://www.google.com/maps/search/?api=1&query=СКК+Блинова+Исилькуль"
```

Open alternatives: Wikimedia Commons, Mapillary, local open-data portals.
