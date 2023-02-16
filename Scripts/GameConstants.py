CHUNK_WIDTH: int = 16
CHUNK_HEIGHT: int = 50
VOID_LEVEL: int = 0
WATER_LEVEL: int = 20

GRAVITY: float = -9.8

TEXTURE_ATLAS_WIDTH_IN_BLOCKS: int = 4
TEXTURE_ATLAS_HEIGHT_IN_BLOCKS: int = 3
TEXTURE_ATLAS_BLOCK_SIZE_X: float = 1.0 / TEXTURE_ATLAS_WIDTH_IN_BLOCKS
TEXTURE_ATLAS_BLOCK_SIZE_Y: float = 1.0 / TEXTURE_ATLAS_HEIGHT_IN_BLOCKS

VERTEX_POSITIONS: list = [
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0),
    (1.0, 1.0, 1.0),
    (0.0, 1.0, 1.0)
]

FACE_NORMALS: list = [
    (0.0, 0.0, -1.0),
    (0.0, 0.0, 1.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (-1.0, 0.0, 0.0),
    (1.0, 0.0, 0.0)
]

FACE_TANGENTS: list = [
    (-1.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
    (0.0, 0.0, -1.0),
    (0.0, 0.0, 1.0)
]

FACE_BITANGENTS: list = [
    (0.0, -1.0, 0.0),
    (0.0, 1.0, 0.0),
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 1.0, 0.0)
]

FACE_INDICES: list = [
    [ 0, 3, 1, 2 ], # Back Face
    [ 5, 6, 4, 7 ], # Front Face
    [ 3, 7, 2, 6 ], # Top Face
    [ 1, 5, 0, 4 ], # Bottom Face
    [ 4, 7, 0, 3 ], # Left Face
    [ 1, 2, 5, 6 ]  # Right Face
]