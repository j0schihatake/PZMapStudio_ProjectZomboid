# Typed building builders

Instead of a generic `build_house`, agents can build a named type:

```bash
python3 -m pzmapstudio.cli build-typed \
  --scene city.json --kind church \
  --x 40 --y 40 --w 160 --h 120 \
  --name "Marshall Church"

python3 -m pzmapstudio.cli build-typed \
  --scene city.json --kind courthouse \
  --x 260 --y 40 --w 200 --h 160 \
  --floors 2 --name "Marshall Courthouse"
```

Kinds:

```text
house
church
courthouse
school
clinic
barn
warehouse
shop
mill
fair_hall
```

Each builder creates:

- outer walls and entrance doors;
- interior partitions with doors;
- type-specific rooms;
- basic furniture (pews/desks/beds/tables/shelves);
- multiple floors where requested.

These are still prototype layouts, not traced real plans. The next step is
per-type furniture/entrance rules and roof access.


Landmark layouts now include nave/altar/vestibule, courtroom A/B, lobby, mill floor/loading dock/mill office, fair exhibition/entrance/stalls, barn stalls and warehouse loading dock.
