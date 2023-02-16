import unittest
from Noise import *
from GameConstants import *
from Block import *
from ChunkDataManager import *
from TerrainGenerator import *

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
        meshData: MeshData = TerrainGenerator.generate_mesh_data(TerrainGenerator.generate_block_map((-1, -1)))
        self.assertIsNotNone(meshData, "Invalid mesh data was returned")
        self.assertEqual(len(meshData.Positions), 9136)
        self.assertEqual(len(meshData.UVs), 9136)
        self.assertEqual(len(meshData.Normals), 9136)
        self.assertEqual(len(meshData.Tangents), 9136)
        self.assertEqual(len(meshData.Bitangents), 9136)
        self.assertEqual(len(meshData.SolidIndices), 10632)
        self.assertEqual(len(meshData.WaterIndices), 3072)
        self.assertEqual(len(meshData.TransparentIndices), 0)

class TestChunkDataManager(unittest.TestCase):
    def test_chunk_data_manager(self):
        try:
            # Test initialization
            ChunkDataManager.initialize(5)
            self.assertEqual(len(ChunkDataManager._DataGenProcesses), 5, "Process count missmatch")
            for process in ChunkDataManager._DataGenProcesses:
                self.assertEqual(process.is_alive(), True, "Process was not started correctly")

            # Test creating chunk data with existing block map
            blockMap: list = TerrainGenerator.generate_block_map((0, 0))
            ChunkDataManager.enqueue_for_update((0, 0), blockMap)
            chunkData: tuple = ChunkDataManager.get_ready_chunk_data(True)
            self.assertIsNotNone(chunkData, "Creating chunk data failed")
            self.assertEqual(chunkData[1].BlockMap, blockMap, "Block map is not the same as the one passed as a parameter")
            self.assertGreater(len(chunkData[1].Mesh.Positions), 0, "Empty positions array")
            self.assertGreater(len(chunkData[1].Mesh.UVs), 0, "Empty UVs array")
            self.assertGreater(len(chunkData[1].Mesh.Normals), 0, "Empty normals array")
            self.assertGreater(len(chunkData[1].Mesh.Tangents), 0, "Empty tangents array")
            self.assertGreater(len(chunkData[1].Mesh.Bitangents), 0, "Empty bitangents array")
            self.assertGreater(len(chunkData[1].Mesh.SolidIndices), 0, "Empty solid indices array")

            # Test creating chunk data with no block map
            ChunkDataManager.enqueue_for_update((0, 0), None)
            chunkData: tuple = ChunkDataManager.get_ready_chunk_data(True)
            self.assertIsNotNone(chunkData, "Creating chunk data failed")
            self.assertGreater(len(chunkData[1].BlockMap), 0, "Empty block map")
            self.assertGreater(len(chunkData[1].Mesh.Positions), 0, "Empty positions array")
            self.assertGreater(len(chunkData[1].Mesh.UVs), 0, "Empty UVs array")
            self.assertGreater(len(chunkData[1].Mesh.Normals), 0, "Empty normals array")
            self.assertGreater(len(chunkData[1].Mesh.Tangents), 0, "Empty tangents array")
            self.assertGreater(len(chunkData[1].Mesh.Bitangents), 0, "Empty bitangents array")
            self.assertGreater(len(chunkData[1].Mesh.SolidIndices), 0, "Empty solid indices array")

            # Test shutdown
            ChunkDataManager.shutdown()
            self.assertEqual(len(ChunkDataManager._DataGenProcesses), 0, "Alive processes after shutdown")
        finally:
            ChunkDataManager.shutdown()

if __name__ == "__main__":
    unittest.main()