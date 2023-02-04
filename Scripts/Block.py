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
                bottomFaceTexID: int, leftFaceTexID: int, rightFaceTexID: int, isSolid: bool, isTransparent: bool) -> None:
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
        return -1