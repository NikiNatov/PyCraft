from Atom import * 
from Noise import *
from Block import *
import random

CHUNK_WIDTH: int = 16
CHUNK_HEIGHT: int = 256
VOID_LEVEL: int = 0
WATER_LEVEL: int = 40
CLOUD_LEVEL: int = 120

class Chunk:
    GridPosition: Vec2
    World: Entity
    _BlockMap: list
    _Vertices: VertexList
    _Indices: Uint32List
    _TotalIndexCount: int
    _Submeshes: SubmeshList
    _ChunkEntity : Entity
    _MeshComponent: MeshComponent

    def __init__(self, gridPosition: Vec2, world: Entity):
        self.GridPosition = gridPosition
        self.World = world
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
        self._MeshComponent.mesh.set_material(0, self.World.get_script().BlockSolidMaterial)
        if len(self._Submeshes) > 1:
            self._MeshComponent.mesh.set_material(1, self.World.get_script().BlockTransparentMaterial)
        if len(self._Submeshes) > 2:
            self._MeshComponent.mesh.set_material(2, self.World.get_script().BlockTransparentMaterial)
        self._MeshComponent.mesh.update_gpu_data(True)

    def create_block_map(self) -> None:
        heights: list = [[0] * CHUNK_WIDTH] * CHUNK_WIDTH

        noise1: Noise = Noise(40713, 6, 110.0, 205.0, 0.38, 18.0)
        noise2: Noise = Noise(40713, 4, 30.0, 200.0, 0.15, 0.0)

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

                        # Trees
                        if x >= 3 and x <= CHUNK_WIDTH - 3 and z >= 3 and z <= CHUNK_WIDTH - 3:
                            value: int = random.randint(1, 95)
                            if value > 90:
                                treeHeight: int = random.randint(4, 6)

                                # Trunk
                                for i in range(treeHeight):
                                    self._BlockMap[x][y + i + 1][z] = BlockType.Wood

                                # Crown
                                for i in range(x - 2, x + 3):
                                    for j in range(z - 2, z + 3):
                                        self._BlockMap[i][y + treeHeight + 1][j] = BlockType.Leaf
                                        self._BlockMap[i][y + treeHeight + 2][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    for j in range(z - 1, z + 2):
                                        self._BlockMap[i][y + treeHeight + 3][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    self._BlockMap[i][y + treeHeight + 3][z] = BlockType.Leaf

                                for i in range(z - 1, z + 2):
                                    self._BlockMap[x][y + treeHeight + 3][i] = BlockType.Leaf
                    elif y < heights[x][z] and y >= heights[x][z] - 5:
                        self._BlockMap[x][y][z] = BlockType.Dirt
                    elif y < heights[x][z] - 5:
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
        waterIndices: list = []

        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if self._BlockMap[x][y][z] != BlockType.Air:
                        self._add_faces(x, y, z, positions, uv, normals, tangents, bitangents, solidIndices, transparentIndices, waterIndices)

        # Create vertex and index arrays
        self._Vertices = VertexList([Vertex()] * len(positions))
        for i in range(len(positions)):
            self._Vertices[i].position = positions[i]
            self._Vertices[i].uv = uv[i]
            self._Vertices[i].normal = normals[i]
            self._Vertices[i].tangent = tangents[i]
            self._Vertices[i].bitangent = bitangents[i]

        self._Indices = Uint32List()
        self._Indices.extend(solidIndices)
        self._Indices.extend(transparentIndices)
        self._Indices.extend(waterIndices)
        
        # Create submeshes
        currentIndexCount: int = 0
        submesh: Submesh = Submesh()
        submesh.start_vertex = 0
        submesh.vertex_count = len(self._Vertices)
        submesh.start_index = currentIndexCount
        submesh.index_count = len(solidIndices)
        submesh.material_index = 0
        self._Submeshes.append(submesh)
        currentIndexCount += len(solidIndices)

        if len(transparentIndices) > 0:
            submesh.start_vertex = 0
            submesh.vertex_count = len(self._Vertices)
            submesh.start_index = currentIndexCount
            submesh.index_count = len(transparentIndices)
            submesh.material_index = len(self._Submeshes)
            self._Submeshes.append(submesh)
            currentIndexCount += len(transparentIndices)

        if len(waterIndices) > 0:
            submesh.start_vertex = 0
            submesh.vertex_count = len(self._Vertices)
            submesh.start_index = currentIndexCount
            submesh.index_count = len(waterIndices)
            submesh.material_index = len(self._Submeshes)
            self._Submeshes.append(submesh)
            currentIndexCount += len(waterIndices)

    def get_block(self, x: int, y: int, z: int) -> BlockType:
        if self._is_block_in_chunk(x, y, z):
            return self._BlockMap[x][y][z]

        return BlockType.Air

    def _add_faces(self, x: int, y: int, z: int, positions: list, uv: list, normals: list, tangents: list, bitangents: list, solidIndices: list, transparentIndices: list, waterIndices: list) -> None:
        blockType: BlockType = self._BlockMap[x][y][z]
        position: Vec3 = Vec3(x, y, z)

        if blockType == BlockType.Water:
            # Only top and bottom face
            for face in range(2, 4):
                # Positions
                positions.append(Vec3(position.x, (position.y - 0.2) if face == 2 else (position.y + 0.8), position.z) + VERTEX_POSITIONS[FACE_INDICES[face][0]])
                positions.append(Vec3(position.x, (position.y - 0.2) if face == 2 else (position.y + 0.8), position.z) + VERTEX_POSITIONS[FACE_INDICES[face][1]])
                positions.append(Vec3(position.x, (position.y - 0.2) if face == 2 else (position.y + 0.8), position.z) + VERTEX_POSITIONS[FACE_INDICES[face][2]])
                positions.append(Vec3(position.x, (position.y - 0.2) if face == 2 else (position.y + 0.8), position.z) + VERTEX_POSITIONS[FACE_INDICES[face][3]])

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
                waterIndices.append(self._TotalIndexCount)
                waterIndices.append(self._TotalIndexCount + 1)
                waterIndices.append(self._TotalIndexCount + 2)
                waterIndices.append(self._TotalIndexCount + 2)
                waterIndices.append(self._TotalIndexCount + 1)
                waterIndices.append(self._TotalIndexCount + 3)
                self._TotalIndexCount += 4
        else:
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