from Noise import *
from GameConstants import *
from Block import *
import random
import operator

class MeshData:
    positions: list
    uvs: list
    normals: list
    tangents: list
    bitangents: list
    solid_indices: list
    transparent_indices: list
    water_indices: list

    def __init__(self) -> None:
        self.positions = []
        self.uvs = []
        self.normals = []
        self.tangents = []
        self.bitangents = []
        self.solid_indices = []
        self.transparent_indices = []
        self.water_indices = []

class TerrainGenerator:
    seed: int = 0
    octaves: int = 4
    scale: float = 20.0
    persistance: float = 0.5
    lacunarity: float = 2.0
    
    def generate_block_map(chunk_grid_coords: tuple) -> list:
        # Create the height for each point of the terrain using noise algorithm
        height_map: list = [0.0] * CHUNK_WIDTH * CHUNK_WIDTH
        for y in range(CHUNK_WIDTH):
            for x in range(CHUNK_WIDTH):
                sample_x: float = (float(x / CHUNK_WIDTH) + chunk_grid_coords[0] + TerrainGenerator.seed) / TerrainGenerator.scale
                sample_Y: float = (float(y / CHUNK_WIDTH) + chunk_grid_coords[1] + TerrainGenerator.seed) / TerrainGenerator.scale
                G: float = 2.0 ** -TerrainGenerator.persistance
                amplitude: float = 1.0
                frequency: float = 1.0
                normalization: float = 0.0
                total_value: float = 0.0
                for i in range(TerrainGenerator.octaves):
                    noise_value: float = Noise.perlin(sample_x * frequency, sample_Y * frequency) * 0.5 + 0.5
                    total_value += noise_value * amplitude
                    normalization += amplitude
                    amplitude *= G
                    frequency *= TerrainGenerator.lacunarity
                total_value /= normalization   
                height_map[y * CHUNK_WIDTH + x] = int(total_value * (CHUNK_HEIGHT - 10))

        # Set the block values based on the height map
        block_map: list = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]
        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if y > height_map[z * CHUNK_WIDTH + x] and y > WATER_LEVEL and block_map[x][y][z] != BlockType.Wood and block_map[x][y][z] != BlockType.Leaf:
                        block_map[x][y][z] = BlockType.Air
                    elif y == WATER_LEVEL and y > height_map[z * CHUNK_WIDTH + x]:
                        block_map[x][y][z] = BlockType.Water
                    elif y > height_map[z * CHUNK_WIDTH + x] and y < WATER_LEVEL:
                        block_map[x][y][z] = BlockType.Air
                    elif y == height_map[z * CHUNK_WIDTH + x] and y < WATER_LEVEL + 2:
                        block_map[x][y][z] = BlockType.Sand
                    elif y == height_map[z * CHUNK_WIDTH + x]:
                        block_map[x][y][z] = BlockType.Grass

                        # Trees
                        if x >= 3 and x <= CHUNK_WIDTH - 3 and z >= 3 and z <= CHUNK_WIDTH - 3:
                            value: int = random.randint(1, 95)
                            if value > 92:
                                tree_height: int = random.randint(4, 6)

                                # Trunk
                                for i in range(tree_height):
                                    block_map[x][y + i + 1][z] = BlockType.Wood

                                # Crown
                                for i in range(x - 2, x + 3):
                                    for j in range(z - 2, z + 3):
                                        block_map[i][y + tree_height + 1][j] = BlockType.Leaf
                                        block_map[i][y + tree_height + 2][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    for j in range(z - 1, z + 2):
                                        block_map[i][y + tree_height + 3][j] = BlockType.Leaf

                                for i in range(x - 1, x + 2):
                                    block_map[i][y + tree_height + 3][z] = BlockType.Leaf

                                for i in range(z - 1, z + 2):
                                    block_map[x][y + tree_height + 3][i] = BlockType.Leaf
                    elif y < height_map[z * CHUNK_WIDTH + x] and y >= height_map[z * CHUNK_WIDTH + x] - 5:
                        block_map[x][y][z] = BlockType.Dirt
                    elif y <= height_map[z * CHUNK_WIDTH + x] - 5:
                        block_map[x][y][z] = BlockType.Stone
        return block_map

    def generate_mesh_data(block_map: list) -> MeshData:
        mesh_data: MeshData = MeshData()
        if block_map is None:
            return mesh_data
        current_index: int = 0
        for x in range(CHUNK_WIDTH):
            for z in range(CHUNK_WIDTH):
                for y in range(CHUNK_HEIGHT):
                    if block_map[x][y][z] != BlockType.Air:
                        block_type: BlockType = block_map[x][y][z]
                        position: tuple = (x, y, z)

                        if block_type == BlockType.Water:
                            # Only top and bottom face
                            for face in range(2, 4):
                                # positions
                                mesh_data.positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][0]])))
                                mesh_data.positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][1]])))
                                mesh_data.positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][2]])))
                                mesh_data.positions.append(tuple(map(operator.add, (position[0], (position[1] - 0.2) if face == 2 else (position[1] + 0.8), position[2]), VERTEX_POSITIONS[FACE_INDICES[face][3]])))

                                # Texture coords
                                mesh_data.uvs.extend(BLOCK_TYPES[block_type].calculate_uvs(BlockFace(face)))

                                # normals
                                mesh_data.normals.append(FACE_NORMALS[face])
                                mesh_data.normals.append(FACE_NORMALS[face])
                                mesh_data.normals.append(FACE_NORMALS[face])
                                mesh_data.normals.append(FACE_NORMALS[face])

                                # tangents
                                mesh_data.tangents.append(FACE_TANGENTS[face])
                                mesh_data.tangents.append(FACE_TANGENTS[face])
                                mesh_data.tangents.append(FACE_TANGENTS[face])
                                mesh_data.tangents.append(FACE_TANGENTS[face])

                                # bitangents
                                mesh_data.bitangents.append(FACE_BITANGENTS[face])
                                mesh_data.bitangents.append(FACE_BITANGENTS[face])
                                mesh_data.bitangents.append(FACE_BITANGENTS[face])
                                mesh_data.bitangents.append(FACE_BITANGENTS[face])

                                # Indices
                                mesh_data.water_indices.append(current_index)
                                mesh_data.water_indices.append(current_index + 1)
                                mesh_data.water_indices.append(current_index + 2)
                                mesh_data.water_indices.append(current_index + 2)
                                mesh_data.water_indices.append(current_index + 1)
                                mesh_data.water_indices.append(current_index + 3)

                                current_index += 4
                        else:
                            for face in range(6):
                                neighbour_block_pos: tuple = tuple(map(operator.add, position, FACE_NORMALS[face]))
                                neighbour_block_type: BlockType = TerrainGenerator._get_block(int(neighbour_block_pos[0]), int(neighbour_block_pos[1]), int(neighbour_block_pos[2]), block_map)

                                if neighbour_block_type == BlockType.Air or BLOCK_TYPES[neighbour_block_type].is_transparent:
                                    # positions
                                    mesh_data.positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][0]])))
                                    mesh_data.positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][1]])))
                                    mesh_data.positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][2]])))
                                    mesh_data.positions.append(tuple(map(operator.add, position, VERTEX_POSITIONS[FACE_INDICES[face][3]])))

                                    # Texture coords
                                    mesh_data.uvs.extend(BLOCK_TYPES[block_type].calculate_uvs(BlockFace(face)))

                                    # normals
                                    mesh_data.normals.append(FACE_NORMALS[face])
                                    mesh_data.normals.append(FACE_NORMALS[face])
                                    mesh_data.normals.append(FACE_NORMALS[face])
                                    mesh_data.normals.append(FACE_NORMALS[face])

                                    # tangents
                                    mesh_data.tangents.append(FACE_TANGENTS[face])
                                    mesh_data.tangents.append(FACE_TANGENTS[face])
                                    mesh_data.tangents.append(FACE_TANGENTS[face])
                                    mesh_data.tangents.append(FACE_TANGENTS[face])

                                    # bitangents
                                    mesh_data.bitangents.append(FACE_BITANGENTS[face])
                                    mesh_data.bitangents.append(FACE_BITANGENTS[face])
                                    mesh_data.bitangents.append(FACE_BITANGENTS[face])
                                    mesh_data.bitangents.append(FACE_BITANGENTS[face])

                                    # Indices
                                    if BLOCK_TYPES[block_type].is_transparent:
                                        mesh_data.transparent_indices.append(current_index)
                                        mesh_data.transparent_indices.append(current_index + 1)
                                        mesh_data.transparent_indices.append(current_index + 2)
                                        mesh_data.transparent_indices.append(current_index + 2)
                                        mesh_data.transparent_indices.append(current_index + 1)
                                        mesh_data.transparent_indices.append(current_index + 3)
                                    else:
                                        mesh_data.solid_indices.append(current_index)
                                        mesh_data.solid_indices.append(current_index + 1)
                                        mesh_data.solid_indices.append(current_index + 2)
                                        mesh_data.solid_indices.append(current_index + 2)
                                        mesh_data.solid_indices.append(current_index + 1)
                                        mesh_data.solid_indices.append(current_index + 3)
                                    current_index += 4
        return mesh_data
    
    def _get_block(x: int, y: int, z: int, block_map: list) -> BlockType:
        if not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH):
            return block_map[x][y][z]
        return BlockType.Air