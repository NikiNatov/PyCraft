from Atom import * 
from Chunk import *

class World(Entity):
    _Chunk: Chunk

    def __init__(self, entityID: int):
        super().__init__(entityID)
        self._Chunk = Chunk(Vec2(0.0, 0.0))

    def on_create(self) -> None:
        self._Chunk.initialize()
        self._Chunk.create_mesh()

    def on_update(self, ts: Timestep) -> None:
        pass