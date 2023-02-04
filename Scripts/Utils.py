from Atom import *
from GameConstants import *
import sys

def get_block_coordinates_in_chunk(blockWorldPosition: Vec3) -> Vec3:
    return Vec3(
        (CHUNK_WIDTH + (int(blockWorldPosition.x) % CHUNK_WIDTH)) % CHUNK_WIDTH,
		(CHUNK_HEIGHT + (int(blockWorldPosition.y) % CHUNK_HEIGHT)) % CHUNK_HEIGHT,
		(CHUNK_WIDTH + (int(blockWorldPosition.z) % CHUNK_WIDTH)) % CHUNK_WIDTH
    )

def get_block_coordinates(blockWorldPosition: Vec3) -> Vec3:
    return Vec3(
        int(Math.floor(blockWorldPosition.x)),
        int(Math.floor(blockWorldPosition.y)),
        int(Math.floor(blockWorldPosition.z))
    )

def get_chunk_grid_coordinates(chunkWorldPosition: Vec3) -> Vec2:
    x: int = int(chunkWorldPosition.x / CHUNK_WIDTH) if chunkWorldPosition.x >= 0 or int(chunkWorldPosition.x) % CHUNK_WIDTH == 0 else int(chunkWorldPosition.x / CHUNK_WIDTH - 1)
    y: int = int(chunkWorldPosition.z / CHUNK_WIDTH) if chunkWorldPosition.z >= 0 or int(chunkWorldPosition.z) % CHUNK_WIDTH == 0 else int(chunkWorldPosition.z / CHUNK_WIDTH - 1)
    return Vec2(x, y)

def ray_cast(origin: Vec3, direction: Vec3, maxDistance: float) -> list:
    # Raycasting algorithm:
	# https://gamedev.stackexchange.com/questions/47362/cast-ray-to-select-block-in-voxel-game

    currentBlockCoords: Vec3 = get_block_coordinates(origin)
    endPoint: Vec3 = origin + direction * maxDistance

    stepX: int = 1 if direction.x > 0.0 else (-1 if direction.x < 0.0 else 0)
    stepY: int = 1 if direction.y > 0.0 else (-1 if direction.y < 0.0 else 0)
    stepZ: int = 1 if direction.z > 0.0 else (-1 if direction.z < 0.0 else 0)

    delta: Vec3 = Vec3(
        min(stepX / (endPoint.x - origin.x), sys.float_info.max) if stepX != 0 else sys.float_info.max,
        min(stepY / (endPoint.y - origin.y), sys.float_info.max) if stepY != 0 else sys.float_info.max,
        min(stepZ / (endPoint.z - origin.z), sys.float_info.max) if stepZ != 0 else sys.float_info.max
    )

    tMaxX: float = delta.x * (1.0 - origin.x + currentBlockCoords.x) if stepX > 0.0 else delta.x * (origin.x - currentBlockCoords.x)
    tMaxY: float = delta.y * (1.0 - origin.y + currentBlockCoords.y) if stepY > 0.0 else delta.y * (origin.y - currentBlockCoords.y)
    tMaxZ: float = delta.z * (1.0 - origin.z + currentBlockCoords.z) if stepZ > 0.0 else delta.z * (origin.z - currentBlockCoords.z)

    intersectedBlocks: list = []

    while len(intersectedBlocks) < maxDistance * 3:
        if tMaxX < tMaxY:
            if tMaxX < tMaxZ:
                tMaxX += delta.x
                currentBlockCoords.x += stepX
            else:
                tMaxZ += delta.z
                currentBlockCoords.z += stepZ
        else:
            if tMaxY < tMaxZ:
                tMaxY += delta.y
                currentBlockCoords.y += stepY
            else:
                tMaxZ += delta.z
                currentBlockCoords.z += stepZ
        if tMaxX > 1.0 and tMaxY > 1.0 and tMaxZ > 1.0:
            break

        intersectedBlocks.append(Vec3(currentBlockCoords.x, currentBlockCoords.y, currentBlockCoords.z))

    return intersectedBlocks