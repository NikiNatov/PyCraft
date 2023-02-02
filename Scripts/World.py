from Atom import * 
from Chunk import *
from ChunkDataManager import *

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
        ChunkDataManager.initialize(1214141532, 4, 20.0, 0.5, 2.0)
        self.Player.transform.translation = Vec3(100, 60, 100)

        playerChunkX: int = int(self.Player.transform.translation.x / CHUNK_WIDTH)
        playerChunkY: int = int(self.Player.transform.translation.z / CHUNK_WIDTH)

        # Generate the chunks in a spiral around the player
        x: int = 0
        y: int = 0
        dx: int = 0
        dy: int = -1
        gridSize: int = self.ChunkRenderDistance * 2
        for i in range(gridSize ** 2):
            if (-gridSize / 2 < x <= gridSize / 2) and (-gridSize / 2 < y <= gridSize / 2):
                self._ActiveChunks[(x + playerChunkX, y + playerChunkY)] = Chunk((x + playerChunkX, y + playerChunkY), self)
                ChunkDataManager.enqueue_for_update((x + playerChunkX, y + playerChunkY), True)
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
                    ChunkDataManager.enqueue_for_update((x, y), True)

        # Process one chunk per frame
        result: tuple = ChunkDataManager.get_ready_chunk_data()
        if result != None:
            chunkCoords: tuple = result[0]
            chunkData: ChunkData = result[1]
            if chunkCoords in self._ActiveChunks:
                self._ActiveChunks[chunkCoords].update_mesh_data(chunkData)
                self._ActiveChunks[chunkCoords].create_mesh()

    def on_destroy(self) -> None:
        self._ActiveChunks.clear()
        ChunkDataManager.shutdown()