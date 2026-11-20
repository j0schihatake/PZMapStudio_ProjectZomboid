from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pzmapstudio.export import export_bundle, export_tmx
from pzmapstudio.render import render
from pzmapstudio.scene import Scene, SceneError, import_knoxmap, import_pz_map


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
