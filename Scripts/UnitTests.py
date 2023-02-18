import unittest
from Noise import Noise
from ChunkDataManager import ChunkDataManager
from TerrainGenerator import TerrainGenerator, MeshData

class TestNoise(unittest.TestCase):
    def test_perlin_noise(self):
        self.assertEqual(Noise.perlin(0.0, 0.0), 0.0)
        self.assertEqual(Noise.perlin(0.2, 0.2), 0.1852843163636828)
        self.assertEqual(Noise.perlin(0.4, 0.4), 0.20498219982798985)
        self.assertEqual(Noise.perlin(0.6, 0.6), 0.10930631319401268)
        self.assertEqual(Noise.perlin(0.8, 0.8), 0.07780454730040054)
        self.assertEqual(Noise.perlin(1.0, 1.0), 0.0)

class TestTerrainGenerator(unittest.TestCase):
    def test_generate_mesh_data(self):
        mesh_data: MeshData = TerrainGenerator.generate_mesh_data(TerrainGenerator.generate_block_map((-1, -1)))
        self.assertIsNotNone(mesh_data, "Invalid mesh data was returned")
        self.assertEqual(len(mesh_data.positions), 9136)
        self.assertEqual(len(mesh_data.uvs), 9136)
        self.assertEqual(len(mesh_data.normals), 9136)
        self.assertEqual(len(mesh_data.tangents), 9136)
        self.assertEqual(len(mesh_data.bitangents), 9136)
        self.assertEqual(len(mesh_data.solid_indices), 10632)
        self.assertEqual(len(mesh_data.water_indices), 3072)
        self.assertEqual(len(mesh_data.transparent_indices), 0)

class TestChunkDataManager(unittest.TestCase):
    def test_chunk_data_manager(self):
        try:
            # Test initialization
            ChunkDataManager.initialize(5)
            self.assertEqual(len(ChunkDataManager._data_gen_processes), 5, "Process count missmatch")
            for process in ChunkDataManager._data_gen_processes:
                self.assertEqual(process.is_alive(), True, "Process was not started correctly")

            # Test creating chunk data with existing block map
            block_map: list = TerrainGenerator.generate_block_map((0, 0))
            ChunkDataManager.enqueue_for_update((0, 0), block_map)
            chunk_data: tuple = ChunkDataManager.get_ready_chunk_data(True)
            self.assertIsNotNone(chunk_data, "Creating chunk data failed")
            self.assertEqual(chunk_data[1].block_map, block_map, "Block map is not the same as the one passed as a parameter")
            self.assertGreater(len(chunk_data[1].mesh.positions), 0, "Empty positions array")
            self.assertGreater(len(chunk_data[1].mesh.uvs), 0, "Empty UVs array")
            self.assertGreater(len(chunk_data[1].mesh.normals), 0, "Empty normals array")
            self.assertGreater(len(chunk_data[1].mesh.tangents), 0, "Empty tangents array")
            self.assertGreater(len(chunk_data[1].mesh.bitangents), 0, "Empty bitangents array")
            self.assertGreater(len(chunk_data[1].mesh.solid_indices), 0, "Empty solid indices array")

            # Test creating chunk data with no block map
            ChunkDataManager.enqueue_for_update((0, 0), None)
            chunk_data: tuple = ChunkDataManager.get_ready_chunk_data(True)
            self.assertIsNotNone(chunk_data, "Creating chunk data failed")
            self.assertGreater(len(chunk_data[1].block_map), 0, "Empty block map")
            self.assertGreater(len(chunk_data[1].mesh.positions), 0, "Empty positions array")
            self.assertGreater(len(chunk_data[1].mesh.uvs), 0, "Empty UVs array")
            self.assertGreater(len(chunk_data[1].mesh.normals), 0, "Empty normals array")
            self.assertGreater(len(chunk_data[1].mesh.tangents), 0, "Empty tangents array")
            self.assertGreater(len(chunk_data[1].mesh.bitangents), 0, "Empty bitangents array")
            self.assertGreater(len(chunk_data[1].mesh.solid_indices), 0, "Empty solid indices array")

            # Test shutdown
            ChunkDataManager.shutdown()
            self.assertEqual(len(ChunkDataManager._data_gen_processes), 0, "Alive processes after shutdown")
        finally:
            ChunkDataManager.shutdown()

if __name__ == "__main__":
    unittest.main()