from Atom import * 
from enum import Enum

class BlockFace(Enum):
    BackFace = 0
    FrontFace = 1
    TopFace = 2
    BottomFace = 3
    LeftFace = 4
    RightFace = 5

class BlockType(Enum):
    Air	= -1
    Grass = 0
    Dirt = 1
    Stone = 2
    Sand = 3
    Wood = 4
    Leaf = 5
    Plank = 6
    Water = 7
    #Glass = 8

class Block:
    Type: BlockType
    IsSolid: bool
    IsTransparent: bool
    BackFaceTexture: int
    FrontFaceTexture: int
    TopFaceTexture: int
    BottomFaceTexture: int
    LeftFaceTexture: int
    RightFaceTexture: int

    def __init__(self, type: BlockType, backFaceTexID: int, frontFaceTexID: int, topFaceTexID: int,
                bottomFaceTexID: int, leftFaceTexID: int, rightFaceTexID: int, isSolid: bool, isTransparent: bool):
        self.Type = type
        self.BackFaceTexture = backFaceTexID
        self.FrontFaceTexture = frontFaceTexID
        self.TopFaceTexture = topFaceTexID
        self.BottomFaceTexture = bottomFaceTexID
        self.LeftFaceTexture = leftFaceTexID
        self.RightFaceTexture = rightFaceTexID
        self.IsSolid = isSolid
        self.IsTransparent = isTransparent

    def get_texture_id(self, face: BlockFace) -> int:
        match face:
            case BlockFace.BackFace:
                return self.BackFaceTexture
            case BlockFace.FrontFace:
                return self.FrontFaceTexture
            case BlockFace.TopFace:
                return self.TopFaceTexture
            case BlockFace.BottomFace:
                return self.BottomFaceTexture
            case BlockFace.LeftFace:
                return self.LeftFaceTexture
            case BlockFace.RightFace:
                return self.RightFaceTexture
        return 0

TEXTURE_ATLAS_SIZE_IN_BLOCKS: int = 4
TEXTURE_ATLAS_BLOCK_SIZE: float = 1.0 / TEXTURE_ATLAS_SIZE_IN_BLOCKS

VERTEX_POSITIONS: list = [
    Vec3(0.0, 0.0, 0.0),
    Vec3(1.0, 0.0, 0.0),
    Vec3(1.0, 1.0, 0.0),
    Vec3(0.0, 1.0, 0.0),
    Vec3(0.0, 0.0, 1.0),
    Vec3(1.0, 0.0, 1.0),
    Vec3(1.0, 1.0, 1.0),
    Vec3(0.0, 1.0, 1.0)
]

FACE_DIRECTIONS: list = [
    Vec3(0.0, 0.0, -1.0),
    Vec3(0.0, 0.0, 1.0),
    Vec3(0.0, 1.0, 0.0),
    Vec3(0.0, -1.0, 0.0),
    Vec3(-1.0, 0.0, 0.0),
    Vec3(1.0, 0.0, 0.0)
]

FACE_TRIANGLES: list = [
    [ 0, 3, 1, 2 ], # Back Face
    [ 5, 6, 4, 7 ], # Front Face
    [ 3, 7, 2, 6 ], # Top Face
    [ 1, 5, 0, 4 ], # Bottom Face
    [ 4, 7, 0, 3 ], # Left Face
    [ 1, 2, 5, 6 ]  # Right Face
]

BLOCK_TYPES: list = [
    Block(BlockType.Grass, 1, 1, 1, 1, 1, 1, True, False),
    Block(BlockType.Dirt, 0, 0, 0, 0, 0, 0, True, False),
    Block(BlockType.Stone, 4, 4, 4, 4, 4, 4, True, False),
    Block(BlockType.Sand, 5, 5, 5, 5, 5, 5, True, False),
    Block(BlockType.Wood, 7, 7, 7, 7, 7, 7, True, False),
    Block(BlockType.Leaf, 2, 2, 2, 2, 2, 2, True, False),
    Block(BlockType.Plank, 3, 3, 3, 3, 3, 3, True, False),
    Block(BlockType.Water, 6, 6, 6, 6, 6, 6, False, True)
    #Block(BlockType.Glass, 49, 49, 49, 49, 49, 49, True, True),
]