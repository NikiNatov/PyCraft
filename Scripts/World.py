from Atom import * 
from Chunk import *

class World(Entity):
    _Chunks: list

    def __init__(self, entityID: int):
        super().__init__(entityID)
        self._Chunks = []
        for x in range(-3, 3):
            for y in range(-3, 3):
                self._Chunks.append(Chunk(Vec2(x, y)))

    def on_create(self) -> None:
        for chunk in self._Chunks:
            chunk.initialize()
            chunk.create_mesh()

    def on_update(self, ts: Timestep) -> None:
        pass