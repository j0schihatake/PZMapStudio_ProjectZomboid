# Install check

```bash
bash tools/check_install.sh \
  ~/Zomboid/mods/omsk-expansion \
  ~/Zomboid/Workshop/OmskExpansion
```

Checks:

- `mod.info`;
- number of map folders and cells;
- duplicate compiled cells;
- `Contents/mods/.../mod.info`;
- `preview.png` exists and is exactly 256x256.
