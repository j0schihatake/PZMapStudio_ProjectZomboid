# Roof/footprint tracing

When an address is missing or ambiguous, use a roof/satellite image as the
reference and trace the silhouette:

1. Open Google Maps (human) or an open satellite/OSM source.
2. Save a screenshot to `references/`.
3. Find tile coordinates of the building in PZMapStudio.
4. Enter the outline points in tile coordinates:

```bash
python3 -m pzmapstudio.cli build-footprint --scene isilkul.json \
  --points "120,80;180,78;190,120;150,140;118,125" \
  --floors 3 --rooms 6 --name "СКК имени Блинова"
python3 -m pzmapstudio.cli add-reference --scene isilkul.json \
  --title "roof" --path references/skk-roof.jpg --kind map \
  --building house-1
```

The building keeps the polygon outline and gets walls, floors, rooms and
furniture inside it. This is the fallback when no facade/floor-plan photo is
available: shape first, details later.

Google imagery is not stored in the mod; the reference stays local and is
stripped before publishing unless the licence allows redistribution.
