from Atom import * 
from Chunk import *
from ChunkDataManager import *
import Utils

class World(Entity):
    BlockSolidMaterial: Material
    BlockTransparentMaterial: Material
    Player: Entity
    ChunkRenderDistance: int
    _ActiveChunks: dict

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.BlockSolidMaterial = Material(0)
        self.BlockTransparentMaterial = Material(0)
        self.Player = Entity(0)
        self.ChunkRenderDistance = 5
        self._ActiveChunks = dict()
        
    def on_create(self) -> None:
        TerrainGenerator.Seed = 1214141532
        ChunkDataManager.initialize()
        self.Player.transform.translation = Vec3(0, 30, 0)

        playerChunkX: int = int(self.Player.transform.translation.x / CHUNK_WIDTH)
        playerChunkY: int = int(self.Player.transform.translation.z / CHUNK_WIDTH)

        # Generate the chunks in a spiral around the player
        x: int = 0
        y: int = 0
        dx: int = 0
        dy: int = -1
        gridSize: int = self.ChunkRenderDistance * 2
        for _ in range(gridSize ** 2):
            if (-gridSize / 2 < x <= gridSize / 2) and (-gridSize / 2 < y <= gridSize / 2):
                self._ActiveChunks[(x + playerChunkX, y + playerChunkY)] = Chunk((x + playerChunkX, y + playerChunkY), self)
                ChunkDataManager.enqueue_for_update((x + playerChunkX, y + playerChunkY), None)
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx
            x, y = x + dx, y + dy

    def on_update(self, ts: Timestep) -> None:
        playerChunkX: int = int(self.Player.transform.translation.x / CHUNK_WIDTH)
        playerChunkY: int = int(self.Player.transform.translation.z / CHUNK_WIDTH)

        # Check if there are any chunks for deletion
        coordsToDelete: list = []
        for coords, _ in self._ActiveChunks.items():
            if coords[0] > playerChunkX + self.ChunkRenderDistance or coords[0] < playerChunkX - self.ChunkRenderDistance or coords[1] > playerChunkY + self.ChunkRenderDistance or coords[1] < playerChunkY - self.ChunkRenderDistance:
                coordsToDelete.append(coords)
        
        for coords in coordsToDelete:
            del self._ActiveChunks[coords]

        # Add the new chunks
        for x in range(playerChunkX - self.ChunkRenderDistance, playerChunkX + self.ChunkRenderDistance):
            for y in range(playerChunkY - self.ChunkRenderDistance, playerChunkY + self.ChunkRenderDistance):
                if (x, y) not in self._ActiveChunks:
                    self._ActiveChunks[(x, y)] = Chunk((x, y), self)
                    ChunkDataManager.enqueue_for_update((x, y), None)

        # Process one chunk per frame
        result: tuple = ChunkDataManager.get_ready_chunk_data()
        if result is not None:
            chunkCoords: tuple = result[0]
            chunkData: ChunkData = result[1]
            if chunkCoords in self._ActiveChunks:
                self._ActiveChunks[chunkCoords].update_data(chunkData)

    def on_destroy(self) -> None:
        self._ActiveChunks.clear()
        ChunkDataManager.shutdown()

    def get_chunk_at_position(self, worldPosition: Vec3) -> Chunk:
        chunkGridCoords: Vec2 = Utils.get_chunk_grid_coordinates(worldPosition)
        return self._ActiveChunks[(chunkGridCoords.x, chunkGridCoords.y)] if (chunkGridCoords.x, chunkGridCoords.y) in self._ActiveChunks else None

    def set_block_at_position(self, worldPosition: Vec3, blockType: BlockType) -> None:
        blockCoords: Vec3 = Utils.get_block_coordinates_in_chunk(worldPosition)
        chunk: Chunk = self.get_chunk_at_position(worldPosition)
        if chunk is not None:
            chunk.set_block(int(blockCoords.x), int(blockCoords.y), int(blockCoords.z), blockType)
            ChunkDataManager.enqueue_for_update(chunk.GridPosition, chunk._BlockMap)

    def get_block_at_position(self, worldPosition: Vec3) -> BlockType:
        blockCoords: Vec3 = Utils.get_block_coordinates_in_chunk(worldPosition)
        chunk: Chunk = self.get_chunk_at_position(worldPosition)
        return chunk.get_block(int(blockCoords.x), int(blockCoords.y), int(blockCoords.z)) if chunk is not None else BlockType.Air
    
    def is_block_solid(self, worldPosition: Vec3) -> bool:
        blockType: BlockType = self.get_block_at_position(worldPosition)
        if BLOCK_TYPES.get(blockType) is None:
            return False
        return BLOCK_TYPES[blockType].IsSolid
