from GameConstants import *
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
    Glass = 8

class Block:
    type: BlockType
    is_solid: bool
    is_transparent: bool
    back_face_texture_id: int
    front_face_texture_id: int
    top_face_texture_id: int
    bottom_face_texture_id: int
    left_face_texture_id: int
    right_face_texture_id: int

    def __init__(self, type: BlockType, back_face_texture_id: int, front_face_texture_id: int, top_face_texture_id: int,
                bottom_face_texture_id: int, left_face_texture_id: int, right_face_texture_id: int, is_solid: bool, is_transparent: bool) -> None:
        self.type = type
        self.back_face_texture_id = back_face_texture_id
        self.front_face_texture_id = front_face_texture_id
        self.top_face_texture_id = top_face_texture_id
        self.bottom_face_texture_id = bottom_face_texture_id
        self.left_face_texture_id = left_face_texture_id
        self.right_face_texture_id = right_face_texture_id
        self.is_solid = is_solid
        self.is_transparent = is_transparent

    def get_texture_id(self, face: BlockFace) -> int:
        match face:
            case BlockFace.BackFace:
                return self.back_face_texture_id
            case BlockFace.FrontFace:
                return self.front_face_texture_id
            case BlockFace.TopFace:
                return self.top_face_texture_id
            case BlockFace.BottomFace:
                return self.bottom_face_texture_id
            case BlockFace.LeftFace:
                return self.left_face_texture_id
            case BlockFace.RightFace:
                return self.right_face_texture_id
        return -1
    
    def calculate_uvs(self, face: BlockFace) -> list:
        texture_id: int = self.get_texture_id(face)
        u: float = (texture_id % TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_X
        v: float = int(texture_id / TEXTURE_ATLAS_WIDTH_IN_BLOCKS) * TEXTURE_ATLAS_BLOCK_SIZE_Y
        uvs: list = []
        uvs.append((u, v))
        uvs.append((u, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
        uvs.append((u + TEXTURE_ATLAS_BLOCK_SIZE_X, v))
        uvs.append((u + TEXTURE_ATLAS_BLOCK_SIZE_X, v + TEXTURE_ATLAS_BLOCK_SIZE_Y))
        return uvs
    
BLOCK_TYPES: dict = {
    BlockType.Grass: Block(BlockType.Grass, 1, 1, 1, 1, 1, 1, True, False),
    BlockType.Dirt: Block(BlockType.Dirt, 0, 0, 0, 0, 0, 0, True, False),
    BlockType.Stone: Block(BlockType.Stone, 4, 4, 4, 4, 4, 4, True, False),
    BlockType.Sand: Block(BlockType.Sand, 5, 5, 5, 5, 5, 5, True, False),
    BlockType.Wood: Block(BlockType.Wood, 7, 7, 7, 7, 7, 7, True, False),
    BlockType.Leaf: Block(BlockType.Leaf, 2, 2, 2, 2, 2, 2, True, False),
    BlockType.Plank: Block(BlockType.Plank, 3, 3, 3, 3, 3, 3, True, False),
    BlockType.Water: Block(BlockType.Water, 6, 6, 6, 6, 6, 6, False, True),
    BlockType.Glass: Block(BlockType.Glass, 8, 8, 8, 8, 8, 8, True, True)
}