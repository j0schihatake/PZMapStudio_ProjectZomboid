# PZ Workshop folder layout

Project Zomboid's Workshop uploader accepts only these folders inside
`Contents/`:

```text
Contents/
  buildings/
  creative/
  mods/
```

A normal mod must therefore live at:

```text
~/Zomboid/Workshop/<ItemName>/
  preview.png                    # 256x256
  Contents/
    mods/
      <ModName>/
        mod.info
        42/
        common/
```

Putting `mod.info` directly into `Contents/` gives:

```text
В вашей папке Contents/ есть нераспознанные папки
```

Stage correctly:

```bash
bash tools/stage_workshop.sh /path/to/PZMapStudioMod PZMapStudio
bash tools/stage_workshop.sh /path/to/omsk-expansion OmskExpansion
```

Preview must be exactly 256x256 PNG and live at the item root.
