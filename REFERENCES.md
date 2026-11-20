# Reference photos for buildings and streets

PZMapStudio can attach visual references to a scene and to a specific building:

```bash
python3 -m pzmapstudio.cli add-reference --scene isilkul.json \
  --title "School on Lenina" --building cell-7-68-b12 \
  --url "https://example.org/photo" --path references/school.jpg \
  --lat 54.99 --lon 71.30 --notes "brick, two storeys, central entrance"
```

Stored fields:

- title, URL and local file path;
- linked building id;
- latitude/longitude;
- free-form notes (materials, floors, entrances, signs).

## Sources and legality

- **User-supplied screenshots** are the simplest and safest.
- **Google Maps/Street View** imagery may be viewed by a human, but its terms
  do not allow bulk scraping or redistributing imagery. Do not bake Google
  imagery into a public mod.
- Prefer open sources for automatic ingestion: OpenStreetMap tags/footprints,
  Mapillary, Wikimedia Commons, local government open data.
- A reference is a design aid. Recreate the massing, proportions, materials and
  details; do not copy copyrighted textures or artwork.

## Workflow

1. Attach reference photos to a building or street.
2. Set footprint, floors, roof shape and entrance side from the photos.
3. Choose PZ tiles closest to the material/colour.
4. Place practical furniture and signs.
5. Compare the PZMapStudio preview against the reference.
6. Remove the reference from the bundle before publishing if it is not openly
   licensed.
