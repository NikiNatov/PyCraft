from Noise import *
from Block import *
import random
import multiprocessing
import operator

CHUNK_WIDTH: int = 16
CHUNK_HEIGHT: int = 50
VOID_LEVEL: int = 0
WATER_LEVEL: int = 20

class ChunkData:
    BlockMap: list
    Positions: list
    UVs: list
    Normals: list
    Tangents: list
    Bitangents: list
    SolidIndices: list
    TransparentIndices: list
    WaterIndices: list

    def __init__(self):
        self.BlockMap = []
        self.Positions = []
        self.UVs = []
        self.Normals = []
        self.Tangents = []
        self.Bitangents = []
        self.SolidIndices = []
        self.TransparentIndices = []
        self.WaterIndices = []

class ChunkDataManager:
    Seed: int = 0
    Octaves: int = 4
    Scale: float = 20.0
    Persistance: float = 0.5
    Lacunarity: float = 2.0
    _DataGenProcesses: list = []
    _ProcessInputQueue: multiprocessing.Queue = multiprocessing.Queue()
    _ProcessOutputQueue: multiprocessing.Queue = multiprocessing.Queue()

    def initialize(seed: int, octaves: int, scale: float, persistance: float, lacunarity: float):
        ChunkDataManager.Seed = seed
        ChunkDataManager.Octaves = octaves
        ChunkDataManager.Scale = max(scale, 0.001)
        ChunkDataManager.Persistance = persistance
        ChunkDataManager.Lacunarity = lacunarity
        
        for _ in range(int(multiprocessing.cpu_count() / 2)):
            process: multiprocessing.Process = multiprocessing.Process(target = ChunkDataManager._chunk_data_generation_loop, args=(ChunkDataManager._ProcessInputQueue, ChunkDataManager._ProcessOutputQueue))
            process.start()
            ChunkDataManager._DataGenProcesses.append(process)

    def shutdown():
        # Insert None inputs so that the the processes exit their while True loop
        for _ in range(len(ChunkDataManager._DataGenProcesses)):
            ChunkDataManager._ProcessInputQueue.put(None)

        for process in ChunkDataManager._DataGenProcesses:
            process.join()

        ChunkDataManager._DataGenProcesses.clear()

    def enqueue_for_update(chunkCoords: tuple, generateBlockMap: bool) -> None:
        ChunkDataManager._ProcessInputQueue.put((chunkCoords, generateBlockMap))

    def get_ready_chunk_data() -> ChunkData:
        try:
            value = ChunkDataManager._ProcessOutputQueue.get_nowait()
            return value
        except:
            return None

    def _chunk_data_generation_loop(inputQueue: multiprocessing.Queue, outputQueue: multiprocessing.Queue) -> None:
        while True:
            result: tuple = inputQueue.get()
            if result == None:
                break
            chunkCoords: tuple = result[0]
            generateBlockMap: bool = result[1]
            chunkData: ChunkData = ChunkDataManager._generate_chunk_data(chunkCoords, generateBlockMap)
            outputQueue.put((chunkCoords, chunkData))

    def _generate_chunk_data(chunkGridCoords: tuple, generateBlockMap: bool) -> ChunkData:
        chunkData: ChunkData = ChunkData()
        if generateBlockMap:
            heightMap: list = [0.0] * CHUNK_WIDTH * CHUNK_WIDTH
            for y in range(CHUNK_WIDTH):
                for x in range(CHUNK_WIDTH):
                    sampleX: float = (float(x / CHUNK_WIDTH) + chunkGridCoords[0] + ChunkDataManager.Seed) / ChunkDataManager.Scale
                    sampleY: float = (float(y / CHUNK_WIDTH) + chunkGridCoords[1] + ChunkDataManager.Seed) / ChunkDataManager.Scale
                    G: float = 2.0 ** -ChunkDataManager.Persistance
                    amplitude: float = 1.0
                    frequency: float = 1.0
                    normalization: float = 0.0
                    totalValue: float = 0.0
                    for i in range(ChunkDataManager.Octaves):
                        noiseValue: float = Noise.perlin(sampleX * frequency, sampleY * frequency) * 0.5 + 0.5
                        totalValue += noiseValue * amplitude
                        normalization += amplitude
                        amplitude *= G
                        frequency *= ChunkDataManager.Lacunarity
                    totalValue /= normalization   
                    heightMap[y * CHUNK_WIDTH + x] = int(totalValue * (CHUNK_HEIGHT - 10))
            chunkData.BlockMap = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]

        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if y > heightMap[z * CHUNK_WIDTH + x] and y > WATER_LEVEL and chunkData.BlockMap[x][y][z] != BlockType.Wood and chunkData.BlockMap[x][y][z] != BlockType.Leaf:
                        chunkData.BlockMap[x][y][z] = BlockType.Air
                    elif y == WATER_LEVEL and y > heightMap[z * CHUNK_WIDTH + x]:
                        chunkData.BlockMap[x][y][z] = BlockType.Water
                    elif y > heightMap[z * CHUNK_WIDTH + x] and y < WATER_LEVEL:
                        chunkData.BlockMap[x][y][z] = BlockType.Air
                    elif y == heightMap[z * CHUNK_WIDTH + x] and y < WATER_LEVEL + 2:
                        chunkData.BlockMap[x][y][z] = BlockType.Sand
                    elif y == heightMap[z * CHUNK_WIDTH + x]:
                        chunkData.BlockMap[x][y][z] = BlockType.Grass

                        # Trees
                        if x >= 3 and x <= CHUNK_WIDTH - 3 and z >= 3 and z <= CHUNK_WIDTH - 3:
                            value: int = random.randint(1, 95)
                            if value > 92:
                                treeHeight: int = random.randint(4, 6)

                                # Trunk
                                for i in range(treeHeight):
                                    chunkData.BlockMap[x][y + i + 1][z] = BlockType.Wood

                                # Crown
                                for i in range(x - 2, x + 3):
                                    for j in range(z - 2, z + 3):
                                        chunkData.BlockMap[i][y + treeHeight + 1][j] = BlockType.Leaf
                                        chunkData.BlockMap[i][y + treeHeight + 2][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    for j in range(z - 1, z + 2):
                                        chunkData.BlockMap[i][y + treeHeight + 3][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    chunkData.BlockMap[i][y + treeHeight + 3][z] = BlockType.Leaf

                                for i in range(z - 1, z + 2):
                                    chunkData.BlockMap[x][y + treeHeight + 3][i] = BlockType.Leaf
                    elif y < heightMap[z * CHUNK_WIDTH + x] and y >= heightMap[z * CHUNK_WIDTH + x] - 5:
                        chunkData.BlockMap[x][y][z] = BlockType.Dirt
                    elif y <= heightMap[z * CHUNK_WIDTH + x] - 5:
                        chunkData.BlockMap[x][y][z] = BlockType.Stone
        
        # Generate the mesh data
        totalIndexCount: int = 0

        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if chunkData.BlockMap[x][y][z] != BlockType.Air:
                        blockType: BlockType = chunkData.BlockMap[x][y][z]
                        position: tuple = (x, y, z)
                
                        if blockType == BlockType.Water:
                            # Only top and bottom face
                            for face in range(2, 4):
                                # Positions
                                chunkData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][0]])))
                                chunkData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][1]])))
                                chunkData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][2]])))
                                chunkData.Positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][3]])))
                
                                # Texture coords
                                textureID: int = BLOCK_TYPES[blockType].get_texture_id(BlockFace(face))
                                u: float = (textureID % TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_X
                                v: float = int(textureID / TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_Y
                                chunkData.UVs.append((u, v))
                                chunkData.UVs.append((u, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
                                chunkData.UVs.append((u + TEXTURE_ATLAS_BLOCK_SIZE_X, v))
                                chunkData.UVs.append((u + TEXTURE_ATLAS_BLOCK_SIZE_X, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
                
                                # Normals
                                chunkData.Normals.append(FACE_NORMALS[face])
                                chunkData.Normals.append(FACE_NORMALS[face])
                                chunkData.Normals.append(FACE_NORMALS[face])
                                chunkData.Normals.append(FACE_NORMALS[face])
                
                                # Tangents
                                chunkData.Tangents.append(FACE_TANGENTS[face])
                                chunkData.Tangents.append(FACE_TANGENTS[face])
                                chunkData.Tangents.append(FACE_TANGENTS[face])
                                chunkData.Tangents.append(FACE_TANGENTS[face])
                
                                # Bitangents
                                chunkData.Bitangents.append(FACE_BITANGENTS[face])
                                chunkData.Bitangents.append(FACE_BITANGENTS[face])
                                chunkData.Bitangents.append(FACE_BITANGENTS[face])
                                chunkData.Bitangents.append(FACE_BITANGENTS[face])
                
                                # Indices
                                chunkData.WaterIndices.append(totalIndexCount)
                                chunkData.WaterIndices.append(totalIndexCount + 1)
                                chunkData.WaterIndices.append(totalIndexCount + 2)
                                chunkData.WaterIndices.append(totalIndexCount + 2)
                                chunkData.WaterIndices.append(totalIndexCount + 1)
                                chunkData.WaterIndices.append(totalIndexCount + 3)

                                totalIndexCount += 4
                        else:
                            for face in range(6):
                                neighbourBlockPos: tuple = tuple(map(operator.add, position, FACE_NORMALS[face]))
                                neighbourBlockType: BlockType = ChunkDataManager._get_block(int(neighbourBlockPos[0]), int(neighbourBlockPos[1]), int(neighbourBlockPos[2]), chunkData.BlockMap)
                
                                if neighbourBlockType == BlockType.Air or BLOCK_TYPES[neighbourBlockType].IsTransparent:
                                    # Positions
                                    chunkData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][0]])))
                                    chunkData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][1]])))
                                    chunkData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][2]])))
                                    chunkData.Positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][3]])))
                
                                    # Texture coords
                                    textureID: int = BLOCK_TYPES[blockType].get_texture_id(BlockFace(face))
                                    u: float = (textureID % TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_X
                                    v: float = int(textureID / TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_Y
                                    chunkData.UVs.append((u, v))
                                    chunkData.UVs.append((u, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
                                    chunkData.UVs.append((u + TEXTURE_ATLAS_BLOCK_SIZE_X, v))
                                    chunkData.UVs.append((u + TEXTURE_ATLAS_BLOCK_SIZE_X, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
                
                                    # Normals
                                    chunkData.Normals.append(FACE_NORMALS[face])
                                    chunkData.Normals.append(FACE_NORMALS[face])
                                    chunkData.Normals.append(FACE_NORMALS[face])
                                    chunkData.Normals.append(FACE_NORMALS[face])

                                    # Tangents
                                    chunkData.Tangents.append(FACE_TANGENTS[face])
                                    chunkData.Tangents.append(FACE_TANGENTS[face])
                                    chunkData.Tangents.append(FACE_TANGENTS[face])
                                    chunkData.Tangents.append(FACE_TANGENTS[face])

                                    # Bitangents
                                    chunkData.Bitangents.append(FACE_BITANGENTS[face])
                                    chunkData.Bitangents.append(FACE_BITANGENTS[face])
                                    chunkData.Bitangents.append(FACE_BITANGENTS[face])
                                    chunkData.Bitangents.append(FACE_BITANGENTS[face])
                
                                    # Indices
                                    if BLOCK_TYPES[blockType].IsTransparent:
                                        chunkData.TransparentIndices.append(totalIndexCount)
                                        chunkData.TransparentIndices.append(totalIndexCount + 1)
                                        chunkData.TransparentIndices.append(totalIndexCount + 2)
                                        chunkData.TransparentIndices.append(totalIndexCount + 2)
                                        chunkData.TransparentIndices.append(totalIndexCount + 1)
                                        chunkData.TransparentIndices.append(totalIndexCount + 3)
                                    else:
                                        chunkData.SolidIndices.append(totalIndexCount)
                                        chunkData.SolidIndices.append(totalIndexCount + 1)
                                        chunkData.SolidIndices.append(totalIndexCount + 2)
                                        chunkData.SolidIndices.append(totalIndexCount + 2)
                                        chunkData.SolidIndices.append(totalIndexCount + 1)
                                        chunkData.SolidIndices.append(totalIndexCount + 3)
                                    totalIndexCount += 4
        return chunkData
    
    def _get_block(x: int, y: int, z: int, blockMap: list) -> BlockType:
        if not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH):
            return blockMap[x][y][z]
        return BlockType.Air