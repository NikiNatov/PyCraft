from Noise import *
from GameConstants import *
from Block import *
import random
import operator

class MeshData:
    Positions: list
    UVs: list
    Normals: list
    Tangents: list
    Bitangents: list
    SolidIndices: list
    TransparentIndices: list
    WaterIndices: list

    def __init__(self) -> None:
        self.Positions = []
        self.UVs = []
        self.Normals = []
        self.Tangents = []
        self.Bitangents = []
        self.SolidIndices = []
        self.TransparentIndices = []
        self.WaterIndices = []

class TerrainGenerator:
    Seed: int = 0
    Octaves: int = 4
    Scale: float = 20.0
    Persistance: float = 0.5
    Lacunarity: float = 2.0
    
    def generate_block_map(chunkGridCoords: tuple) -> list:
        # Create the height for each point of the terrain using noise algorithm
        heightMap: list = [0.0] * CHUNK_WIDTH * CHUNK_WIDTH
        for y in range(CHUNK_WIDTH):
            for x in range(CHUNK_WIDTH):
                sampleX: float = (float(x / CHUNK_WIDTH) + chunkGridCoords[0] + TerrainGenerator.Seed) / TerrainGenerator.Scale
                sampleY: float = (float(y / CHUNK_WIDTH) + chunkGridCoords[1] + TerrainGenerator.Seed) / TerrainGenerator.Scale
                G: float = 2.0 ** -TerrainGenerator.Persistance
                amplitude: float = 1.0
                frequency: float = 1.0
                normalization: float = 0.0
                totalValue: float = 0.0
                for i in range(TerrainGenerator.Octaves):
                    noiseValue: float = Noise.perlin(sampleX * frequency, sampleY * frequency) * 0.5 + 0.5
                    totalValue += noiseValue * amplitude
                    normalization += amplitude
                    amplitude *= G
                    frequency *= TerrainGenerator.Lacunarity
                totalValue /= normalization   
                heightMap[y * CHUNK_WIDTH + x] = int(totalValue * (CHUNK_HEIGHT - 10))

        # Set the block values based on the height map
        blockMap: list = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]
        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if y > heightMap[z * CHUNK_WIDTH + x] and y > WATER_LEVEL and blockMap[x][y][z] != BlockType.Wood and blockMap[x][y][z] != BlockType.Leaf:
                        blockMap[x][y][z] = BlockType.Air
                    elif y == WATER_LEVEL and y > heightMap[z * CHUNK_WIDTH + x]:
                        blockMap[x][y][z] = BlockType.Water
                    elif y > heightMap[z * CHUNK_WIDTH + x] and y < WATER_LEVEL:
                        blockMap[x][y][z] = BlockType.Air
                    elif y == heightMap[z * CHUNK_WIDTH + x] and y < WATER_LEVEL + 2:
                        blockMap[x][y][z] = BlockType.Sand
                    elif y == heightMap[z * CHUNK_WIDTH + x]:
                        blockMap[x][y][z] = BlockType.Grass

                        # Trees
                        if x >= 3 and x <= CHUNK_WIDTH - 3 and z >= 3 and z <= CHUNK_WIDTH - 3:
                            value: int = random.randint(1, 95)
                            if value > 92:
                                treeHeight: int = random.randint(4, 6)

                                # Trunk
                                for i in range(treeHeight):
                                    blockMap[x][y + i + 1][z] = BlockType.Wood

                                # Crown
                                for i in range(x - 2, x + 3):
                                    for j in range(z - 2, z + 3):
                                        blockMap[i][y + treeHeight + 1][j] = BlockType.Leaf
                                        blockMap[i][y + treeHeight + 2][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    for j in range(z - 1, z + 2):
                                        blockMap[i][y + treeHeight + 3][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    blockMap[i][y + treeHeight + 3][z] = BlockType.Leaf

                                for i in range(z - 1, z + 2):
                                    blockMap[x][y + treeHeight + 3][i] = BlockType.Leaf
                    elif y < heightMap[z * CHUNK_WIDTH + x] and y >= heightMap[z * CHUNK_WIDTH + x] - 5:
                        blockMap[x][y][z] = BlockType.Dirt
                    elif y <= heightMap[z * CHUNK_WIDTH + x] - 5:
                        blockMap[x][y][z] = BlockType.Stone
        return blockMap

    def generate_mesh_data(blockMap: list) -> MeshData:
        meshData: MeshData = MeshData()
        if blockMap is None:
            return meshData
        currentIndex: int = 0
        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if blockMap[x][y][z] != BlockType.Air:
                        blockType: BlockType = blockMap[x][y][z]
                        position: tuple = (x, y, z)

                        if blockType == BlockType.Water:
                            # Only top and bottom face
                            for face in range(2, 4):
                                # Positions
                                meshData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][0]])))
                                meshData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][1]])))
                                meshData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][2]])))
                                meshData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][3]])))

                                # Texture coords
                                meshData.UVs.extend(BLOCK_TYPES[blockType].calculate_uvs(BlockFace(face)))

                                # Normals
                                meshData.Normals.append(FACE_NORMALS[face])
                                meshData.Normals.append(FACE_NORMALS[face])
                                meshData.Normals.append(FACE_NORMALS[face])
                                meshData.Normals.append(FACE_NORMALS[face])

                                # Tangents
                                meshData.Tangents.append(FACE_TANGENTS[face])
                                meshData.Tangents.append(FACE_TANGENTS[face])
                                meshData.Tangents.append(FACE_TANGENTS[face])
                                meshData.Tangents.append(FACE_TANGENTS[face])

                                # Bitangents
                                meshData.Bitangents.append(FACE_BITANGENTS[face])
                                meshData.Bitangents.append(FACE_BITANGENTS[face])
                                meshData.Bitangents.append(FACE_BITANGENTS[face])
                                meshData.Bitangents.append(FACE_BITANGENTS[face])

                                # Indices
                                meshData.WaterIndices.append(currentIndex)
                                meshData.WaterIndices.append(currentIndex + 1)
                                meshData.WaterIndices.append(currentIndex + 2)
                                meshData.WaterIndices.append(currentIndex + 2)
                                meshData.WaterIndices.append(currentIndex + 1)
                                meshData.WaterIndices.append(currentIndex + 3)

                                currentIndex += 4
                        else:
                            for face in range(6):
                                neighbourBlockPos: tuple = tuple(map(operator.add, position, FACE_NORMALS[face]))
                                neighbourBlockType: BlockType = TerrainGenerator._get_block(int(neighbourBlockPos[0]), int(neighbourBlockPos[1]), int(neighbourBlockPos[2]), blockMap)

                                if neighbourBlockType == BlockType.Air or BLOCK_TYPES[neighbourBlockType].IsTransparent:
                                    # Positions
                                    meshData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][0]])))
                                    meshData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][1]])))
                                    meshData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][2]])))
                                    meshData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][3]])))

                                    # Texture coords
                                    meshData.UVs.extend(BLOCK_TYPES[blockType].calculate_uvs(BlockFace(face)))

                                    # Normals
                                    meshData.Normals.append(FACE_NORMALS[face])
                                    meshData.Normals.append(FACE_NORMALS[face])
                                    meshData.Normals.append(FACE_NORMALS[face])
                                    meshData.Normals.append(FACE_NORMALS[face])

                                    # Tangents
                                    meshData.Tangents.append(FACE_TANGENTS[face])
                                    meshData.Tangents.append(FACE_TANGENTS[face])
                                    meshData.Tangents.append(FACE_TANGENTS[face])
                                    meshData.Tangents.append(FACE_TANGENTS[face])

                                    # Bitangents
                                    meshData.Bitangents.append(FACE_BITANGENTS[face])
                                    meshData.Bitangents.append(FACE_BITANGENTS[face])
                                    meshData.Bitangents.append(FACE_BITANGENTS[face])
                                    meshData.Bitangents.append(FACE_BITANGENTS[face])

                                    # Indices
                                    if BLOCK_TYPES[blockType].IsTransparent:
                                        meshData.TransparentIndices.append(currentIndex)
                                        meshData.TransparentIndices.append(currentIndex + 1)
                                        meshData.TransparentIndices.append(currentIndex + 2)
                                        meshData.TransparentIndices.append(currentIndex + 2)
                                        meshData.TransparentIndices.append(currentIndex + 1)
                                        meshData.TransparentIndices.append(currentIndex + 3)
                                    else:
                                        meshData.SolidIndices.append(currentIndex)
                                        meshData.SolidIndices.append(currentIndex + 1)
                                        meshData.SolidIndices.append(currentIndex + 2)
                                        meshData.SolidIndices.append(currentIndex + 2)
                                        meshData.SolidIndices.append(currentIndex + 1)
                                        meshData.SolidIndices.append(currentIndex + 3)
                                    currentIndex += 4
        return meshData
    
    def _get_block(x: int, y: int, z: int, blockMap: list) -> BlockType:
        if not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH):
            return blockMap[x][y][z]
        return BlockType.Air