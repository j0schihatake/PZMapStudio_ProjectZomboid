# Procedural beautify pass

`tools/beautify_map.py` adds practical street furniture to compiled cells:

- bench every 25 road-adjacent squares;
- outdoor lamp every 75;
- bin next to each lamp;
- skips roads, walls, occupied squares and buildings;
- copies untouched cells, so no map holes;
- preserves room/building headers.

Large maps use:

```bash
python3 tools/beautify_parallel.py \
  --source-map "/path/to/map" \
  --out examples/beautify-map \
  --workers 6 --memory-gb 3
```

Each cell is a separate, memory-capped process. A lock file prevents two
beautify writers from corrupting the same output:

```text
examples/beautify-map/.beautify.lock
```

Current pass:

```text
Isilkul       168 / 168  done
Omsk          930 / 930  done
Krasnodar     ~655 / 837
Novosibirsk   ~365 / 1014
Moscow        ~205 / 868
```

The final mod is only updated after a city finishes and is validated.
