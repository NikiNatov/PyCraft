from Atom import *
from GameConstants import *
import sys
import math

def get_block_coordinates_in_chunk(block_world_position: Vec3) -> Vec3:
    return Vec3(
        # We need to use math.fmod() for the C-style mod here instead of % to get the correct result
        math.fmod(CHUNK_WIDTH + math.fmod(Math.floor(block_world_position.x), CHUNK_WIDTH), CHUNK_WIDTH),
        math.fmod(CHUNK_HEIGHT + math.fmod(Math.floor(block_world_position.y), CHUNK_HEIGHT), CHUNK_HEIGHT),
        math.fmod(CHUNK_WIDTH + math.fmod(Math.floor(block_world_position.z), CHUNK_WIDTH), CHUNK_WIDTH)
    )

def get_block_coordinates(block_world_position: Vec3) -> Vec3:
    return Vec3(Math.floor(block_world_position.x), Math.floor(block_world_position.y), Math.floor(block_world_position.z))

def get_chunk_grid_coordinates(chunk_world_position: Vec3) -> Vec2:
    return Vec2(Math.floor(chunk_world_position.x / CHUNK_WIDTH), Math.floor(chunk_world_position.z / CHUNK_WIDTH))

def ray_cast(origin: Vec3, direction: Vec3, max_distance: float) -> list:
    # Raycasting algorithm:
	# https://gamedev.stackexchange.com/questions/47362/cast-ray-to-select-block-in-voxel-game
    current_block_coords: Vec3 = get_block_coordinates(origin)
    end_point: Vec3 = origin + direction * max_distance

    step_x: int = 1 if direction.x > 0.0 else (-1 if direction.x < 0.0 else 0)
    step_y: int = 1 if direction.y > 0.0 else (-1 if direction.y < 0.0 else 0)
    step_z: int = 1 if direction.z > 0.0 else (-1 if direction.z < 0.0 else 0)

    delta: Vec3 = Vec3(
        min(step_x / (end_point.x - origin.x), sys.float_info.max) if step_x != 0 else sys.float_info.max,
        min(step_y / (end_point.y - origin.y), sys.float_info.max) if step_y != 0 else sys.float_info.max,
        min(step_z / (end_point.z - origin.z), sys.float_info.max) if step_z != 0 else sys.float_info.max
    )

    t_max_x: float = delta.x * (1.0 - origin.x + current_block_coords.x) if step_x > 0.0 else delta.x * (origin.x - current_block_coords.x)
    t_max_y: float = delta.y * (1.0 - origin.y + current_block_coords.y) if step_y > 0.0 else delta.y * (origin.y - current_block_coords.y)
    t_max_z: float = delta.z * (1.0 - origin.z + current_block_coords.z) if step_z > 0.0 else delta.z * (origin.z - current_block_coords.z)

    intersected_blocks: list = []

    while len(intersected_blocks) < max_distance * 3:
        if t_max_x < t_max_y:
            if t_max_x < t_max_z:
                t_max_x += delta.x
                current_block_coords.x += step_x
            else:
                t_max_z += delta.z
                current_block_coords.z += step_z
        else:
            if t_max_y < t_max_z:
                t_max_y += delta.y
                current_block_coords.y += step_y
            else:
                t_max_z += delta.z
                current_block_coords.z += step_z
        if t_max_x > 1.0 and t_max_y > 1.0 and t_max_z > 1.0:
            break

        intersected_blocks.append(Vec3(current_block_coords.x, current_block_coords.y, current_block_coords.z))

    return intersected_blocks