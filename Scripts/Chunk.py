from Atom import * 
from ChunkDataManager import *
from Block import *

class Chunk:
    GridPosition: tuple
    World: Entity
    _BlockMap: list
    _ChunkEntity : Entity
    _MeshComponent: MeshComponent

    def __init__(self, gridPosition: tuple, world: Entity) -> None:
        self.GridPosition = gridPosition
        self.World = world
        self._BlockMap = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]
        self._ChunkEntity = Entity.create_entity("Chunk {},{}".format(self.GridPosition[0], self.GridPosition[1]))
        self._ChunkEntity.transform.translation = Vec3(self.GridPosition[0] * CHUNK_WIDTH, 0.0, self.GridPosition[1] * CHUNK_WIDTH)
        self._MeshComponent = self._ChunkEntity.add_mesh_component()

    def __del__(self) -> None:
        Entity.delete_entity(self._ChunkEntity)

    def on_create(self) -> None:
        self._ChunkEntity = Entity.create_entity("Chunk {},{}".format(self.GridPosition[0], self.GridPosition[1]))
        self._ChunkEntity.transform.translation = Vec3(self.GridPosition[0] * CHUNK_WIDTH, 0.0, self.GridPosition[1] * CHUNK_WIDTH)
        self._MeshComponent = self._ChunkEntity.add_mesh_component()

    def update_data(self, chunkData: ChunkData) -> None:
        # Init the block map
        self._BlockMap = chunkData.BlockMap

        # Create index array
        indices: list = []
        indices.extend(chunkData.SolidIndices)
        indices.extend(chunkData.TransparentIndices)
        indices.extend(chunkData.WaterIndices)

        # Create submeshes
        submeshes: list = []
        currentIndexCount: int = 0
        vertexCount: int = len(chunkData.Positions)
        solidSubmesh: Submesh = Submesh()
        solidSubmesh.start_vertex = 0
        solidSubmesh.vertex_count = vertexCount
        solidSubmesh.start_index = currentIndexCount
        solidSubmesh.index_count = len(chunkData.SolidIndices)
        solidSubmesh.material_index = 0
        submeshes.append(solidSubmesh)
        currentIndexCount += len(chunkData.SolidIndices)

        if len(chunkData.TransparentIndices) > 0:
            transparentSubmesh: Submesh = Submesh()
            transparentSubmesh.start_vertex = 0
            transparentSubmesh.vertex_count = vertexCount
            transparentSubmesh.start_index = currentIndexCount
            transparentSubmesh.index_count = len(chunkData.TransparentIndices)
            transparentSubmesh.material_index = len(submeshes)
            submeshes.append(transparentSubmesh)
            currentIndexCount += len(chunkData.TransparentIndices)

        if len(chunkData.WaterIndices) > 0:
            waterSubmesh: Submesh = Submesh()
            waterSubmesh.start_vertex = 0
            waterSubmesh.vertex_count = vertexCount
            waterSubmesh.start_index = currentIndexCount
            waterSubmesh.index_count = len(chunkData.WaterIndices)
            waterSubmesh.material_index = len(submeshes)
            submeshes.append(waterSubmesh)
            currentIndexCount += len(chunkData.WaterIndices)

        self._MeshComponent.mesh = Mesh()
        self._MeshComponent.mesh.set_positions(chunkData.Positions)
        self._MeshComponent.mesh.set_uvs(chunkData.UVs)
        self._MeshComponent.mesh.set_normals(chunkData.Normals)
        self._MeshComponent.mesh.set_tangents(chunkData.Tangents)
        self._MeshComponent.mesh.set_bitangents(chunkData.Bitangents)
        self._MeshComponent.mesh.set_indices(indices)
        self._MeshComponent.mesh.set_submeshes(submeshes)
        self._MeshComponent.mesh.set_material(0, self.World.BlockSolidMaterial)
        if len(submeshes) > 1:
            self._MeshComponent.mesh.set_material(1, self.World.BlockTransparentMaterial)
        if len(submeshes) > 2:
            self._MeshComponent.mesh.set_material(2, self.World.BlockTransparentMaterial)
        self._MeshComponent.mesh.update_gpu_data(True)

    def get_block(self, x: int, y: int, z: int) -> BlockType:
        if self._is_block_in_chunk(x, y, z):
            return self._BlockMap[x][y][z]
        return BlockType.Air

    def _is_block_in_chunk(self, x: int, y: int, z: int) -> bool:
        return not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH)