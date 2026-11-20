"""Command line entry point."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import build_catalog, Catalog
from .export import export_bundle, export_tmx
from .render import render
from .scene import Scene, SceneError, import_knoxmap, import_pz_map, import_pz_region


def _rect(value: str) -> tuple[int, int, int, int]:
    parts = [int(part) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("rect must be x,y,w,h")
    return tuple(parts)  # type: ignore[return-value]


def _load(path: str) -> Scene:
    return Scene.load(path)


def _save(scene: Scene, path: str) -> None:
    scene.save(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pzmapstudio")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new")
    new.add_argument("--name", default="Untitled")
    new.add_argument("--width", type=int, default=512)
    new.add_argument("--height", type=int, default=512)
    new.add_argument("--out", required=True)

    paint = sub.add_parser("paint")
    paint.add_argument("--scene", required=True)
    paint.add_argument("--layer", default="terrain")
    paint.add_argument("--rect", type=_rect, required=True)
    paint.add_argument("--tile", required=True)

    erase = sub.add_parser("erase")
    erase.add_argument("--scene", required=True)
    erase.add_argument("--layer", default="terrain")
    erase.add_argument("--rect", type=_rect, required=True)

    house = sub.add_parser("build-house")
    house.add_argument("--scene", required=True)
    house.add_argument("--x", type=int, required=True)
    house.add_argument("--y", type=int, required=True)
    house.add_argument("--w", type=int, required=True)
    house.add_argument("--h", type=int, required=True)
    house.add_argument("--floors", type=int, default=1)
    house.add_argument("--rooms", type=int, default=4)
    house.add_argument("--no-furnish", action="store_true")
    house.add_argument("--name", default="")

    floor = sub.add_parser("add-floor")
    floor.add_argument("--scene", required=True)
    floor.add_argument("--building", required=True)
    floor.add_argument("--z", type=int, required=True)
    floor.add_argument("--rooms", type=int, default=4)

    furniture = sub.add_parser("place-furniture")
    furniture.add_argument("--scene", required=True)
    furniture.add_argument("--building", required=True)
    furniture.add_argument("--x", type=int, required=True)
    furniture.add_argument("--y", type=int, required=True)
    furniture.add_argument("--z", type=int, default=0)
    furniture.add_argument("--kind", default="chair")

    story = sub.add_parser("add-story")
    story.add_argument("--scene", required=True)
    story.add_argument("--x", type=int, required=True)
    story.add_argument("--y", type=int, required=True)
    story.add_argument("--w", type=int, default=1)
    story.add_argument("--h", type=int, default=1)
    story.add_argument("--kind", default="story")
    story.add_argument("--name", default="")

    spawn = sub.add_parser("add-spawn")
    spawn.add_argument("--scene", required=True)
    spawn.add_argument("--x", type=int, required=True)
    spawn.add_argument("--y", type=int, required=True)
    spawn.add_argument("--z", type=int, default=0)
    spawn.add_argument("--profession", default="unemployed")

    batch = sub.add_parser("apply-batch")
    batch.add_argument("--scene", required=True)
    batch.add_argument("--commands", required=True, help="JSON array of commands")

    undo = sub.add_parser("undo")
    undo.add_argument("--scene", required=True)
    redo = sub.add_parser("redo")
    redo.add_argument("--scene", required=True)

    preview = sub.add_parser("render")
    preview.add_argument("--scene", required=True)
    preview.add_argument("--out", required=True)
    preview.add_argument("--floor", type=int, default=0)

    export = sub.add_parser("export")
    export.add_argument("--scene", required=True)
    export.add_argument("--out", required=True)
    export.add_argument("--tmx", action="store_true")

    import_pz = sub.add_parser("import-knoxmap")
    import_pz.add_argument("--pzw", required=True)
    import_pz.add_argument("--spawnpoints", default=None)
    import_pz.add_argument("--out", required=True)

    import_map = sub.add_parser("import-pz-map")
    import_map.add_argument("--map", required=True)
    import_map.add_argument("--out", required=True)
    import_map.add_argument("--name", default=None)

    import_region = sub.add_parser("import-pz-region")
    import_region.add_argument("--map", required=True)
    import_region.add_argument("--x", type=int, required=True)
    import_region.add_argument("--y", type=int, required=True)
    import_region.add_argument("--width", type=int, required=True)
    import_region.add_argument("--height", type=int, required=True)
    import_region.add_argument("--out", required=True)
    import_region.add_argument("--name", default=None)
    import_region.add_argument("--max-level", type=int, default=0)
    import_region.add_argument("--step", type=int, default=1)

    catalog = sub.add_parser("build-catalog")
    catalog.add_argument("--pz-root", required=True,
                         help="ProjectZomboid/projectzomboid directory")
    catalog.add_argument("--out", required=True)

    search = sub.add_parser("search-catalog")
    search.add_argument("--catalog", required=True)
    search.add_argument("--kind", choices=["all", "tiles", "items", "stories"],
                        default="all")
    search.add_argument("--query", default="")
    search.add_argument("--limit", type=int, default=50)

    api = sub.add_parser("serve")
    api.add_argument("--scene", required=True)
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8765)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            Scene(name=args.name, width=args.width, height=args.height).save(args.out)
            print(args.out)
        elif args.command == "paint":
            scene = _load(args.scene)
            print(scene.apply({"op": "paint", "layer": args.layer, "x": args.rect[0],
                               "y": args.rect[1], "w": args.rect[2], "h": args.rect[3],
                               "tile": args.tile}))
            _save(scene, args.scene)
        elif args.command == "erase":
            scene = _load(args.scene)
            print(scene.apply({"op": "erase", "layer": args.layer, "x": args.rect[0],
                               "y": args.rect[1], "w": args.rect[2], "h": args.rect[3]}))
            _save(scene, args.scene)
        elif args.command == "build-house":
            scene = _load(args.scene)
            print(scene.apply({
                "op": "build_house", "x": args.x, "y": args.y, "w": args.w,
                "h": args.h, "floors": args.floors, "rooms": args.rooms,
                "furnish": not args.no_furnish, "name": args.name,
            }))
            _save(scene, args.scene)
        elif args.command == "add-floor":
            scene = _load(args.scene)
            print(scene.apply({"op": "add_floor", "building": args.building,
                               "z": args.z, "rooms": args.rooms}))
            _save(scene, args.scene)
        elif args.command == "place-furniture":
            scene = _load(args.scene)
            print(scene.apply({"op": "place_furniture", "building": args.building,
                               "x": args.x, "y": args.y, "z": args.z,
                               "kind": args.kind}))
            _save(scene, args.scene)
        elif args.command == "add-story":
            scene = _load(args.scene)
            print(scene.apply({"op": "add_story", "x": args.x, "y": args.y,
                               "w": args.w, "h": args.h, "kind": args.kind,
                               "name": args.name}))
            _save(scene, args.scene)
        elif args.command == "add-spawn":
            scene = _load(args.scene)
            print(scene.apply({"op": "add_spawn", "x": args.x, "y": args.y,
                               "z": args.z, "profession": args.profession}))
            _save(scene, args.scene)
        elif args.command == "apply-batch":
            scene = _load(args.scene)
            commands = json.loads(Path(args.commands).read_text(encoding="utf-8"))
            print(scene.apply_batch(commands))
            _save(scene, args.scene)
        elif args.command in ("undo", "redo"):
            scene = _load(args.scene)
            print(scene.apply({"op": args.command}))
            _save(scene, args.scene)
        elif args.command == "render":
            scene = _load(args.scene)
            print(render(scene, args.out, floor=args.floor))
        elif args.command == "export":
            scene = _load(args.scene)
            print(export_bundle(scene, args.out))
            if args.tmx:
                print(export_tmx(scene, Path(args.out) / "scene.tmx"))
        elif args.command == "import-knoxmap":
            scene = import_knoxmap(args.pzw, args.spawnpoints)
            scene.save(args.out)
            print(json.dumps(scene.stats(), indent=2))
        elif args.command == "import-pz-map":
            scene = import_pz_map(args.map, args.name)
            scene.save(args.out)
            print(json.dumps(scene.stats(), indent=2))
        elif args.command == "import-pz-region":
            scene = import_pz_region(args.map, args.x, args.y, args.width,
                                     args.height, args.name, args.max_level, args.step)
            scene.save(args.out)
            print(json.dumps(scene.stats(), indent=2))
        elif args.command == "build-catalog":
            catalog = build_catalog(args.pz_root)
            catalog.save(args.out)
            print(json.dumps({"tiles": len(set(catalog.tiles)),
                              "items": len(set(catalog.items)),
                              "stories": len(catalog.stories)}, indent=2))
        elif args.command == "search-catalog":
            catalog = Catalog.load(args.catalog)
            print(json.dumps(catalog.search(args.kind, args.query, args.limit),
                             indent=2, ensure_ascii=False))
        elif args.command == "serve":
            from .api import serve
            serve(args.scene, host=args.host, port=args.port)
        return 0
    except (SceneError, OSError, ValueError) as error:
        parser.error(str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
