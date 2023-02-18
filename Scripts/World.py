from Atom import *
from GameConstants import *
from Chunk import Chunk
from ChunkDataManager import ChunkDataManager
from TerrainGenerator import TerrainGenerator
from Block import BlockType, BLOCK_TYPES
import Utils

class World(Entity):
    block_solid_material: Material
    block_transparent_material: Material
    player: Entity
    chunk_render_distance: int
    _active_chunks: dict

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.block_solid_material = Material(0)
        self.block_transparent_material = Material(0)
        self.player = Entity(0)
        self.chunk_render_distance = 5
        self._active_chunks = dict()
        
    def on_create(self) -> None:
        TerrainGenerator.seed = 1214141532
        ChunkDataManager.initialize()
        self.player.transform.translation = Vec3(0, 50, 0)

        player_chunk_x: int = int(self.player.transform.translation.x / CHUNK_WIDTH)
        player_chunk_y: int = int(self.player.transform.translation.z / CHUNK_WIDTH)

        # Generate the chunks in a spiral around the player
        x: int = 0
        y: int = 0
        dx: int = 0
        dy: int = -1
        grid_size: int = self.chunk_render_distance * 2
        for _ in range(grid_size ** 2):
            if (-grid_size / 2 < x <= grid_size / 2) and (-grid_size / 2 < y <= grid_size / 2):
                self._active_chunks[(x + player_chunk_x, y + player_chunk_y)] = Chunk((x + player_chunk_x, y + player_chunk_y), self)
                ChunkDataManager.enqueue_for_update((x + player_chunk_x, y + player_chunk_y), None)
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx
            x, y = x + dx, y + dy

    def on_update(self, ts: Timestep) -> None:
        player_chunk_x: int = int(self.player.transform.translation.x / CHUNK_WIDTH)
        player_chunk_y: int = int(self.player.transform.translation.z / CHUNK_WIDTH)

        # Check if there are any chunks for deletion
        coords_to_delete: list = []
        for coords, _ in self._active_chunks.items():
            if coords[0] > player_chunk_x + self.chunk_render_distance or coords[0] < player_chunk_x - self.chunk_render_distance or coords[1] > player_chunk_y + self.chunk_render_distance or coords[1] < player_chunk_y - self.chunk_render_distance:
                coords_to_delete.append(coords)
        
        for coords in coords_to_delete:
            del self._active_chunks[coords]

        # Add the new chunks
        for x in range(player_chunk_x - self.chunk_render_distance, player_chunk_x + self.chunk_render_distance):
            for y in range(player_chunk_y - self.chunk_render_distance, player_chunk_y + self.chunk_render_distance):
                if (x, y) not in self._active_chunks:
                    self._active_chunks[(x, y)] = Chunk((x, y), self)
                    ChunkDataManager.enqueue_for_update((x, y), None)

        # Process one chunk per frame
        result: tuple = ChunkDataManager.get_ready_chunk_data()
        if result is not None:
            chunk_coords: tuple = result[0]
            chunk_data: ChunkData = result[1]
            if chunk_coords in self._active_chunks:
                self._active_chunks[chunk_coords].update_data(chunk_data)

    def on_destroy(self) -> None:
        self._active_chunks.clear()
        ChunkDataManager.shutdown()

    def get_chunk_at_position(self, world_position: Vec3) -> Chunk:
        chunk_grid_coords: Vec2 = Utils.get_chunk_grid_coordinates(world_position)
        return self._active_chunks[(chunk_grid_coords.x, chunk_grid_coords.y)] if (chunk_grid_coords.x, chunk_grid_coords.y) in self._active_chunks else None

    def set_block_at_position(self, world_position: Vec3, block_type: BlockType) -> None:
        block_coords: Vec3 = Utils.get_block_coordinates_in_chunk(world_position)
        chunk: Chunk = self.get_chunk_at_position(world_position)
        if chunk is not None:
            chunk.set_block(int(block_coords.x), int(block_coords.y), int(block_coords.z), block_type)
            ChunkDataManager.enqueue_for_update(chunk.grid_position, chunk._block_map)

    def get_block_at_position(self, world_position: Vec3) -> BlockType:
        block_coords: Vec3 = Utils.get_block_coordinates_in_chunk(world_position)
        chunk: Chunk = self.get_chunk_at_position(world_position)
        return chunk.get_block(int(block_coords.x), int(block_coords.y), int(block_coords.z)) if chunk is not None else BlockType.Air
    
    def is_block_solid(self, world_position: Vec3) -> bool:
        block_type: BlockType = self.get_block_at_position(world_position)
        if BLOCK_TYPES.get(block_type) is None:
            return False
        return BLOCK_TYPES[block_type].is_solid
