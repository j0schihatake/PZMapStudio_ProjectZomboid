# New-game errors

## Fixed: EOFException in lotheader

Cause: generated cells lacked the 1024-byte zombie intensity table after
rooms/buildings.

Fix: `worlded` writes the table; existing Trumbull/SoD2 headers patched.

## Fixed: duplicate RoomDef.metaID

Cause: the same room footprint existed on more than one floor.

Fix: the cell writer emits each room origin once; affected headers were
re-exported.

## Fixed: NullPointerException lotHeader2

Cause: a missing cell inside the Novosibirsk map bounding box (170 holes).

Fix: blank grass cells were written for every hole; Novosibirsk is now a
complete 37x32 cell rectangle (1184 cells).

## Long load

The combined world is ~7,800 cells across 11 maps. First new-save load can take
minutes, especially on a hard disk. This is expected, not a crash.
