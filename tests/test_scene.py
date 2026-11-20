from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pzmapstudio.address import google_maps_url, parse_nominatim, footprint_dimensions
from pzmapstudio.audit import audit_scene
from pzmapstudio.catalog import build_catalog
from pzmapstudio.guide import format_help
from pzmapstudio.export import apply_scene_objects, export_bundle, export_pz_region, export_tmx
from pzmapstudio.render import render
from pzmapstudio.scene import Scene, SceneError, import_knoxmap, import_pz_map, import_pz_region


class SceneTests(unittest.TestCase):
    def test_build_house_floors_furniture_spawn(self):
        scene = Scene(width=200, height=200)
        result = scene.apply({
            "op": "build_house", "x": 10, "y": 10, "w": 80, "h": 60,
            "floors": 3, "rooms": 6,
        })
        self.assertEqual(result["floors"], 3)
        self.assertEqual(scene.stats()["buildings"], 1)
        self.assertEqual(scene.stats()["floors"], 3)
        self.assertGreater(scene.stats()["furniture"], 0)
        scene.apply({"op": "add_spawn", "x": 50, "y": 80})
        self.assertEqual(len(scene.spawns), 1)

    def test_add_floor_and_furniture(self):
        scene = Scene(width=100, height=100)
        scene.apply({"op": "build_house", "x": 10, "y": 10, "w": 30, "h": 30,
                     "floors": 1, "rooms": 1})
        scene.apply({"op": "add_floor", "building": "house-1", "z": 5, "rooms": 2})
        self.assertIn(5, scene.buildings["house-1"].floors)
        scene.apply({"op": "place_furniture", "building": "house-1",
                     "x": 15, "y": 15, "z": 5, "kind": "lamp"})
        self.assertTrue(any(f.kind == "lamp" for f in scene.buildings["house-1"].floors[5].furniture))

    def test_reference(self):
        scene = Scene(width=100, height=100)
        scene.apply({"op": "build_house", "x": 10, "y": 10, "w": 20, "h": 20})
        scene.apply({"op": "add_reference", "title": "photo", "url": "https://example.org",
                     "building": "house-1", "notes": "brick", "kind": "floorplan"})
        self.assertEqual(scene.references[0].title, "photo")
        self.assertEqual(scene.references[0].kind, "floorplan")
        with self.assertRaises(SceneError):
            scene.apply({"op": "add_reference", "title": "bad", "building": "missing"})

    def test_clean_interiors(self):
        scene = Scene(width=100, height=100)
        scene.paint("terrain", 0, 0, 100, 100, "grass")
        scene.apply({"op": "build_house", "x": 20, "y": 20, "w": 30, "h": 30,
                     "floors": 1, "rooms": 2})
        self.assertTrue(any(kind["kind"] == "outdoor-ground-inside"
                            for kind in audit_scene(scene)["issues"]))
        scene.apply({"op": "clean_interiors"})
        self.assertFalse(any(kind["kind"] == "outdoor-ground-inside"
                             for kind in audit_scene(scene)["issues"]))

    def test_art_pass(self):
        scene = Scene(width=100, height=100)
        scene.paint("terrain", 0, 0, 100, 100, "grass")
        scene.apply({"op": "build_house", "x": 10, "y": 10, "w": 40, "h": 40,
                     "floors": 2, "rooms": 4})
        result = scene.apply({"op": "art_pass", "min_roof_area": 120})
        self.assertGreater(result["roofs"]["added"], 0)
        self.assertFalse(any(kind["kind"] == "outdoor-ground-inside"
                             for kind in audit_scene(scene)["issues"]))

    def test_polygon_footprint(self):
        scene = Scene(width=100, height=100)
        result = scene.apply({"op": "build_footprint",
                              "points": [[10, 10], [50, 10], [55, 30], [30, 40], [10, 35]],
                              "floors": 2})
        self.assertEqual(result["points"], 5)
        self.assertIn("house-1", scene.buildings)
        self.assertGreater(len(scene.buildings["house-1"].outline), 2)

    def test_fence_gate_gap(self):
        scene = Scene(width=30, height=30)
        scene.apply({"op": "add_fence", "x": 5, "y": 5, "length": 10,
                     "axis": "x", "gate": True,
                     "tile": "fixtures_doors_fences_01_0"})
        self.assertEqual(len(scene.layers["objects"]), 9)
        self.assertNotIn((10, 5), scene.layers["objects"])

    def test_fence_tile_object_pass(self):
        from pzmapstudio.pzlot import read_cell_records, write_cell
        scene = Scene(width=256, height=256)
        scene.apply({"op": "add_fence", "x": 10, "y": 10, "length": 5,
                     "axis": "x", "tile": "fixtures_doors_fences_01_0"})
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            out = Path(td) / "out"
            write_cell(src, 0, 0, {(10, 10): "grass"})
            apply_scene_objects(src, scene, out, 0, 0)
            names = [names for x, y, z, room, names in read_cell_records(out, 0, 0)
                     if (x, y, z) == (10, 10, 0)]
            self.assertTrue(names)
            self.assertIn("fixtures_doors_fences_01_0", names[0])

    def test_place_object(self):
        scene = Scene(width=20, height=20)
        scene.apply({"op": "place_object", "x": 5, "y": 6,
                     "tile": "furniture_tables_01_0"})
        self.assertEqual(scene.layers["objects"][(5, 6)], "furniture_tables_01_0")

    def test_road_and_fence(self):
        scene = Scene(width=100, height=100)
        scene.apply({"op": "add_road", "x": 5, "y": 5, "w": 80, "h": 10,
                     "material": "asphalt", "sidewalk": True})
        self.assertEqual(len(scene.layers["roads"]), 800)
        self.assertEqual(len(scene.layers["sidewalks"]), 160)
        scene.apply({"op": "add_fence", "x": 3, "y": 20, "length": 30,
                     "axis": "x", "kind": "picket", "gate": True})
        self.assertEqual(len(scene.fences), 1)

    def test_paint_and_erase(self):
        scene = Scene(width=100, height=100)
        scene.paint("roads", 0, 0, 100, 10, "asphalt")
        self.assertEqual(len(scene.layers["roads"]), 1000)
        scene.erase("roads", 0, 0, 10, 10)
        self.assertEqual(len(scene.layers["roads"]), 900)

    def test_out_of_bounds(self):
        scene = Scene(width=50, height=50)
        with self.assertRaises(SceneError):
            scene.paint("roads", 45, 45, 10, 10, "asphalt")

    def test_undo_redo(self):
        scene = Scene(width=100, height=100)
        scene.apply({"op": "build_house", "x": 10, "y": 10, "w": 20, "h": 20})
        self.assertEqual(scene.stats()["buildings"], 1)
        scene.apply({"op": "undo"})
        self.assertEqual(scene.stats()["buildings"], 0)
        scene.apply({"op": "redo"})
        self.assertEqual(scene.stats()["buildings"], 1)

    def test_save_load(self):
        scene = Scene(name="x", width=64, height=64)
        scene.apply({"op": "add_spawn", "x": 5, "y": 6})
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "scene.json"
            scene.save(path)
            loaded = Scene.load(path)
            self.assertEqual(loaded.stats(), scene.stats())
            self.assertEqual(loaded.spawns[0].x, 5)


class ExportTests(unittest.TestCase):
    def test_export_bundle_and_tmx(self):
        scene = Scene(name="test", width=64, height=64)
        scene.apply({"op": "build_house", "x": 4, "y": 4, "w": 16, "h": 16})
        scene.apply({"op": "add_spawn", "x": 10, "y": 10})
        with tempfile.TemporaryDirectory() as td:
            out = export_bundle(scene, Path(td) / "bundle")
            self.assertTrue((out / "map.info").exists())
            self.assertIn("posX = 10", (out / "spawnpoints.lua").read_text())
            tmx = export_tmx(scene, Path(td) / "scene.tmx")
            self.assertIn("<map", tmx.read_text())

    def test_pz_terrain_roundtrip(self):
        scene = Scene(width=256, height=256)
        scene.apply({"op": "add_road", "x": 0, "y": 100, "w": 256, "h": 16,
                     "material": "blends_street_01_64", "sidewalk": True})
        with tempfile.TemporaryDirectory() as td:
            out = export_pz_region(scene, Path(td) / "map", 0, 0)
            loaded = import_pz_region(out, 0, 0, 256, 256)
            self.assertEqual(loaded.width, 256)
            self.assertGreater(len(loaded.layers["roads"]), 0)

    def test_render(self):
        scene = Scene(name="test", width=64, height=64)
        scene.apply({"op": "add_spawn", "x": 10, "y": 10})
        with tempfile.TemporaryDirectory() as td:
            out = render(scene, Path(td) / "preview.png")
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 100)

    def test_import_pz_folder(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "map"
            folder.mkdir()
            (folder / "0_0.lotheader").write_text("")
            (folder / "1_2.lotheader").write_text("")
            (folder / "spawnpoints.lua").write_text(
                "function SpawnPoints() return { unemployed = { { posX = 10, posY = 20, posZ = 0 } } } end"
            )
            scene = import_pz_map(folder)
            self.assertEqual(scene.width, 512)
            self.assertEqual(scene.height, 768)
            self.assertEqual(len(scene.spawns), 1)

    def test_import_knoxmap(self):
        pzw = """<?xml version=\"1.0\"?><world version=\"1.0\" width=\"2\" height=\"3\"/>"""
        spawn = "function SpawnPoints() return { unemployed = { { posX = 10, posY = 20, posZ = 0 } } } end"
        with tempfile.TemporaryDirectory() as td:
            pzw_path = Path(td) / "x.pzw"
            sp_path = Path(td) / "spawnpoints.lua"
            pzw_path.write_text(pzw)
            sp_path.write_text(spawn)
            scene = import_knoxmap(pzw_path, sp_path)
            self.assertEqual(scene.width, 600)
            self.assertEqual(scene.height, 900)
            self.assertEqual(len(scene.spawns), 1)


if __name__ == "__main__":
    unittest.main()


class PzLotTests(unittest.TestCase):
    def test_classify_street(self):
        from pzmapstudio.pzlot import classify_tile
        self.assertEqual(classify_tile(["blends_street_01_69"]), ("roads", "blends_street_01_69"))
        self.assertEqual(classify_tile(["grass_01_0"]), ("terrain", "grass_01_0"))
        self.assertEqual(classify_tile(["water_01_0"]), ("water", "water_01_0"))


class CatalogTests(unittest.TestCase):
    def test_catalog_parser(self):
        with tempfile.TemporaryDirectory() as td:
            media = Path(td) / "media"
            (media / "tile_definitions").mkdir(parents=True)
            (media / "scripts").mkdir()
            (media / "lua/server/RandomizedWorldContent/StoryClutter").mkdir(parents=True)
            (media / "tile_definitions/test.tiles.txt").write_text(
                "tileset\n{\n  file = test\n  // test_0\n  // test_1\n}\n"
            )
            (media / "scripts/items.txt").write_text("item Axe\n{\n}\n")
            (media / "lua/server/RandomizedWorldContent/StoryClutter/StoryClutter_Definitions.lua").write_text(
                'StoryClutter.Murder = {\n    "Base.Knife",\n    "Base.Blood",\n}\n'
            )
            catalog = build_catalog(Path(td))
            self.assertIn("test_0", catalog.tiles)
            self.assertIn("Base.Axe", catalog.items)
            self.assertEqual(len(catalog.stories["Murder"]), 2)


class AddressTests(unittest.TestCase):
    def test_google_url(self):
        self.assertIn("google.com/maps", google_maps_url("Исилькуль"))

    def test_nominatim_shape(self):
        result = parse_nominatim("x", [{"display_name": "x", "lat": "55", "lon": "71",
                                        "boundingbox": ["54.99", "55.0", "71.2", "71.21"],
                                        "extratags": {"building:levels": "3"}}])
        self.assertEqual(result.lat, 55.0)
        dims = footprint_dimensions(result)
        self.assertEqual(dims["floors"], 3)
        self.assertGreater(dims["width_tiles"], 0)


class RewriteTests(unittest.TestCase):
    def test_rewrite_preserves_header(self):
        from pzmapstudio.pzlot import read_header_full, rewrite_cell, write_cell, read_cell_records
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            out = Path(td) / "out"
            write_cell(src, 0, 0, {(1, 1): "grass"})
            before = read_header_full(src / "0_0.lotheader")
            rewrite_cell(src, out, 0, 0, {(1, 1, 0): ["grass"]})
            after = read_header_full(out / "0_0.lotheader")
            self.assertEqual(before[0].names, after[0].names)
            self.assertTrue((out / "world_0_0.lotpack").exists())


class HelpTests(unittest.TestCase):
    def test_help_lists_commands(self):
        text = format_help()
        self.assertIn("PZMapStudio", text)
        self.assertIn("build-footprint", text)
        self.assertIn("apply-object-pass", text)
