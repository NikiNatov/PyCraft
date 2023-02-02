from Atom import * 
from ChunkDataManager import *
from Block import *

class Chunk:
    GridPosition: tuple
    World: Entity
    _BlockMap: list
    _Positions: list
    _UVs: list
    _Normals: list
    _Tangents: list
    _Bitangents: list
    _Indices: list
    _Submeshes: list
    _ChunkEntity : Entity
    _MeshComponent: MeshComponent

    def __init__(self, gridPosition: tuple, world: Entity) -> None:
        self.GridPosition = gridPosition
        self.World = world
        self._BlockMap = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]
        self._Positions = []
        self._UVs = []
        self._Normals = []
        self._Tangents = []
        self._Bitangents = []
        self._Indices = []
        self._Submeshes = []
        self._ChunkEntity = Entity.create_entity("Chunk {},{}".format(self.GridPosition[0], self.GridPosition[1]))
        self._ChunkEntity.transform.translation = Vec3(self.GridPosition[0] * CHUNK_WIDTH, 0.0, self.GridPosition[1] * CHUNK_WIDTH)
        self._MeshComponent = self._ChunkEntity.add_mesh_component()

    def __del__(self) -> None:
        Entity.delete_entity(self._ChunkEntity)

    def on_create(self) -> None:
        self._ChunkEntity = Entity.create_entity("Chunk {},{}".format(self.GridPosition[0], self.GridPosition[1]))
        self._ChunkEntity.transform.translation = Vec3(self.GridPosition[0] * CHUNK_WIDTH, 0.0, self.GridPosition[1] * CHUNK_WIDTH)
        self._MeshComponent = self._ChunkEntity.add_mesh_component()

    def create_mesh(self):
        self._MeshComponent.mesh = Mesh()
        self._MeshComponent.mesh.set_positions(self._Positions)
        self._MeshComponent.mesh.set_uvs(self._UVs)
        self._MeshComponent.mesh.set_normals(self._Normals)
        self._MeshComponent.mesh.set_tangents(self._Tangents)
        self._MeshComponent.mesh.set_bitangents(self._Bitangents)
        self._MeshComponent.mesh.set_indices(self._Indices)
        self._MeshComponent.mesh.set_submeshes(self._Submeshes)
        self._MeshComponent.mesh.set_material(0, self.World.BlockSolidMaterial)
        if len(self._Submeshes) > 1:
            self._MeshComponent.mesh.set_material(1, self.World.BlockTransparentMaterial)
        if len(self._Submeshes) > 2:
            self._MeshComponent.mesh.set_material(2, self.World.BlockTransparentMaterial)
        self._MeshComponent.mesh.update_gpu_data(True)

    def update_mesh_data(self, chunkData: ChunkData) -> None:
        self._MeshComponent.mesh = Mesh()
        self._Positions = []
        self._UVs = []
        self._Normals = []
        self._Tangents = []
        self._Bitangents = []
        self._Indices = []
        self._Submeshes = []

        # Create vertex and index arrays
        vertexCount: int = len(chunkData.Positions)
        for _ in range(vertexCount):
            self._Positions = chunkData.Positions
            self._UVs = chunkData.UVs
            self._Normals = chunkData.Normals
            self._Tangents = chunkData.Tangents
            self._Bitangents = chunkData.Bitangents

        self._Indices.extend(chunkData.SolidIndices)
        self._Indices.extend(chunkData.TransparentIndices)
        self._Indices.extend(chunkData.WaterIndices)

        # Create submeshes
        currentIndexCount: int = 0
        solidSubmesh: Submesh = Submesh()
        solidSubmesh.start_vertex = 0
        solidSubmesh.vertex_count = vertexCount
        solidSubmesh.start_index = currentIndexCount
        solidSubmesh.index_count = len(chunkData.SolidIndices)
        solidSubmesh.material_index = 0
        self._Submeshes.append(solidSubmesh)
        currentIndexCount += len(chunkData.SolidIndices)

        if len(chunkData.TransparentIndices) > 0:
            transparentSubmesh: Submesh = Submesh()
            transparentSubmesh.start_vertex = 0
            transparentSubmesh.vertex_count = vertexCount
            transparentSubmesh.start_index = currentIndexCount
            transparentSubmesh.index_count = len(chunkData.TransparentIndices)
            transparentSubmesh.material_index = len(self._Submeshes)
            self._Submeshes.append(transparentSubmesh)
            currentIndexCount += len(chunkData.TransparentIndices)

        if len(chunkData.WaterIndices) > 0:
            waterSubmesh: Submesh = Submesh()
            waterSubmesh.start_vertex = 0
            waterSubmesh.vertex_count = vertexCount
            waterSubmesh.start_index = currentIndexCount
            waterSubmesh.index_count = len(chunkData.WaterIndices)
            waterSubmesh.material_index = len(self._Submeshes)
            self._Submeshes.append(waterSubmesh)
            currentIndexCount += len(chunkData.WaterIndices)

    def get_block(self, x: int, y: int, z: int) -> BlockType:
        if self._is_block_in_chunk(x, y, z):
            return self._BlockMap[x][y][z]
        return BlockType.Air

    def _is_block_in_chunk(self, x: int, y: int, z: int) -> bool:
        return not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH)