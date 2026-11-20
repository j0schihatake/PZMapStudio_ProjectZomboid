# PZ Workshop folder layout

Project Zomboid's Workshop uploader requires:

```text
~/Zomboid/Workshop/<ItemName>/
  Contents/
    mod.info
    42/
    common/
```

The mod files must be inside `Contents/`; putting them directly in
`~/Zomboid/Workshop/<ItemName>/` gives:

```text
В выбранной папке нет папки Contents/
```

Stage a built mod:

```bash
bash tools/stage_workshop.sh \
  /path/to/PZMapStudioMod \
  PZMapStudio
```

For maps:

```bash
bash tools/stage_workshop.sh \
  /path/to/omsk-expansion \
  OmskExpansion
```

Then main menu → Workshop → select the item folder.
