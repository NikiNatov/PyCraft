from Atom import * 
from Noise import *
from Block import *

CHUNK_WIDTH: int = 16
CHUNK_HEIGHT: int = 256
VOID_LEVEL: int = 0
WATER_LEVEL: int = 40
CLOUD_LEVEL: int = 120

class Chunk:
    GridPosition: Vec2
    _BlockMap: list
    _Vertices: VertexList
    _Indices: Uint32List
    _TotalIndexCount: int
    _Submeshes: SubmeshList
    _ChunkEntity : Entity
    _MeshComponent: MeshComponent

    def __init__(self, gridPosition: Vec2):
        self.GridPosition = gridPosition
        self._BlockMap = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]
        self._Vertices = VertexList()
        self._Indices = Uint32List()
        self._TotalIndexCount = 0
        self._Submeshes: SubmeshList()
        self._ChunkEntity = Entity(0)
        self._MeshComponent = MeshComponent()

    def initialize(self) -> None:
        self._ChunkEntity = Entity.create_entity("Chunk {},{}".format(self.GridPosition.x, self.GridPosition.y))
        self._ChunkEntity.transform.translation = Vec3(self.GridPosition.x * CHUNK_WIDTH, 0.0, self.GridPosition.y * CHUNK_WIDTH)
        self._MeshComponent = self._ChunkEntity.add_mesh_component()
        self.create_block_map()
        self.update_mesh_data()

    def create_mesh(self):
        self._MeshComponent.mesh = Mesh()
        self._MeshComponent.mesh.vertices = self._Vertices
        self._MeshComponent.mesh.indices = self._Indices
        self._MeshComponent.mesh.submeshes = self._Submeshes
        self._MeshComponent.mesh.set_material(0, Material.find("Materials/BlocksMaterialSolid.atmmat"))
        self._MeshComponent.mesh.set_material(1, Material.find("Materials/BlocksMaterialTransparent.atmmat"))
        self._MeshComponent.mesh.update_gpu_data(True)

    def create_block_map(self) -> None:
        heights: list = [[0] * CHUNK_WIDTH] * CHUNK_WIDTH

        noise1: Noise = Noise(12412412414, 6, 110.0, 205.0, 0.38, 18.0)
        noise2: Noise = Noise(12412412414, 4, 30.0, 200.0, 1.15, 0.0)

        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                blockGlobalX: float = x + self.GridPosition.x * CHUNK_WIDTH
                blockGlobalZ: float = z + self.GridPosition.y * CHUNK_WIDTH
                value1: float = noise1.get_noise(blockGlobalX, blockGlobalZ)
                value2: float = noise2.get_noise(blockGlobalX, blockGlobalZ)
                finalResult: float = value1 * value2
                heights[x][z] = int(finalResult * noise1.Amplitude + noise1.Offset)

        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if y > heights[x][z] and y > WATER_LEVEL and self._BlockMap[x][y][z] != BlockType.Wood and self._BlockMap[x][y][z] != BlockType.Leaf:
                        self._BlockMap[x][y][z] = BlockType.Air
                    elif y == WATER_LEVEL and y > heights[x][z]:
                        self._BlockMap[x][y][z] = BlockType.Water
                    elif y > heights[x][z] and y < WATER_LEVEL:
                        self._BlockMap[x][y][z] = BlockType.Air
                    elif y == heights[x][z] and y < WATER_LEVEL + 2:
                        self._BlockMap[x][y][z] = BlockType.Sand
                    elif y == heights[x][z]:
                        self._BlockMap[x][y][z] = BlockType.Grass
                    elif y < heights[x][z] and y >= heights[x][z] - 5:
                        self._BlockMap[x][y][z] = BlockType.Dirt
                    else:
                        self._BlockMap[x][y][z] = BlockType.Stone

    def update_mesh_data(self) -> None:
        self._MeshComponent.mesh = Mesh()
        self._Vertices = VertexList()
        self._Indices = Uint32List()
        self._TotalIndexCount = 0
        self._Submeshes = SubmeshList()

        positions: list = []
        uv: list = []
        normals: list = []
        tangents: list = []
        bitangents: list = []
        solidIndices: list = []
        transparentIndices: list = []

        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if self._BlockMap[x][y][z] != BlockType.Air:
                        self._add_faces(x, y, z, positions, uv, normals, tangents, bitangents, solidIndices, transparentIndices)

        # Create vertex and index arrays
        self._Vertices = VertexList([Vertex()] * len(positions))
        for i in range(len(positions)):
            self._Vertices[i].position = positions[i]
            self._Vertices[i].uv = uv[i]
            self._Vertices[i].normal = normals[i]
            self._Vertices[i].tangent = tangents[i]
            self._Vertices[i].bitangent = bitangents[i]

        self._Indices = Uint32List()
        for i in range(len(solidIndices)):
            self._Indices.append(solidIndices[i])
        for i in range(len(transparentIndices)):
            self._Indices.append(transparentIndices[i])
        
        # Create submeshes
        self._Submeshes = SubmeshList([Submesh()] * 2)
        self._Submeshes[0].start_vertex = 0
        self._Submeshes[0].vertex_count = len(self._Vertices)
        self._Submeshes[0].start_index = 0
        self._Submeshes[0].index_count = len(solidIndices)
        self._Submeshes[0].material_index = 0

        self._Submeshes[1].start_vertex = 0
        self._Submeshes[1].vertex_count = len(self._Vertices)
        self._Submeshes[1].start_index = len(solidIndices)
        self._Submeshes[1].index_count = len(transparentIndices)
        self._Submeshes[1].material_index = 1

    def get_block(self, x: int, y: int, z: int) -> BlockType:
        if self._is_block_in_chunk(x, y, z):
            return self._BlockMap[x][y][z]

        return BlockType.Air

    def _add_faces(self, x: int, y: int, z: int, positions: list, uv: list, normals: list, tangents: list, bitangents: list, solidIndices: list, transparentIndices: list) -> None:
        blockType: BlockType = self._BlockMap[x][y][z]
        position: Vec3 = Vec3(x, y, z)
        
        for face in range(6):
            neighbourBlockPos: Vec3 = position + FACE_NORMALS[face]
            neighbourBlockType: BlockType = self.get_block(int(neighbourBlockPos.x), int(neighbourBlockPos.y), int(neighbourBlockPos.z))

            if neighbourBlockType == BlockType.Air or BLOCK_TYPES[neighbourBlockType].IsTransparent:
                # Positions
                positions.append(position + VERTEX_POSITIONS[FACE_INDICES[face][0]])
                positions.append(position + VERTEX_POSITIONS[FACE_INDICES[face][1]])
                positions.append(position + VERTEX_POSITIONS[FACE_INDICES[face][2]])
                positions.append(position + VERTEX_POSITIONS[FACE_INDICES[face][3]])

                # Texture coords
                textureID: int = BLOCK_TYPES[blockType].get_texture_id(BlockFace(face))
                u: float = (textureID % TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_X
                v: float = int(textureID / TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_Y

                uv.append(Vec2(u, v))
                uv.append(Vec2(u, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
                uv.append(Vec2(u + TEXTURE_ATLAS_BLOCK_SIZE_X, v))
                uv.append(Vec2(u + TEXTURE_ATLAS_BLOCK_SIZE_X, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))

                # Normals
                normals.append(FACE_NORMALS[face])
                normals.append(FACE_NORMALS[face])
                normals.append(FACE_NORMALS[face])
                normals.append(FACE_NORMALS[face])

                # Tangents
                tangents.append(FACE_TANGENTS[face])
                tangents.append(FACE_TANGENTS[face])
                tangents.append(FACE_TANGENTS[face])
                tangents.append(FACE_TANGENTS[face])

                # Bitangents
                bitangents.append(FACE_BITANGENTS[face])
                bitangents.append(FACE_BITANGENTS[face])
                bitangents.append(FACE_BITANGENTS[face])
                bitangents.append(FACE_BITANGENTS[face])

                # Indices
                if BLOCK_TYPES[blockType].IsTransparent:
                    transparentIndices.append(self._TotalIndexCount)
                    transparentIndices.append(self._TotalIndexCount + 1)
                    transparentIndices.append(self._TotalIndexCount + 2)
                    transparentIndices.append(self._TotalIndexCount + 2)
                    transparentIndices.append(self._TotalIndexCount + 1)
                    transparentIndices.append(self._TotalIndexCount + 3)
                else:
                    solidIndices.append(self._TotalIndexCount)
                    solidIndices.append(self._TotalIndexCount + 1)
                    solidIndices.append(self._TotalIndexCount + 2)
                    solidIndices.append(self._TotalIndexCount + 2)
                    solidIndices.append(self._TotalIndexCount + 1)
                    solidIndices.append(self._TotalIndexCount + 3)
                self._TotalIndexCount += 4

    def _is_block_in_chunk(self, x: int, y: int, z: int) -> bool:
        return not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH)