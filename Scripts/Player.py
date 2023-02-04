from Atom import *
from Block import *
from ChunkDataManager import *
from Chunk import *
from World import *

import Utils

class Player(Entity):
    JumpForce: float
    GravityForce: float
    MovementSpeed: float
    BlockBreakRange: float
    World: Entity
    Camera: Entity
    _IsInAir: bool
    _IsUnderWater: bool
    _PrevMousePos: Vec2
    _Velocity: Vec3

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.JumpForce = 10.0
        self.GravityForce = -20.0
        self.MovementSpeed = 7.0
        self.BlockBreakRange = 5.0
        self.World = Entity(0)
        self.Camera = Entity(0)
        self._IsInAir = False
        self._IsUnderWater = True
        self._Velocity = Vec3(0.0, 0.0, 0.0)

    def on_create(self) -> None:
        pass

    def on_update(self, ts: Timestep) -> None:
        if self._IsUnderWater:
            self._Velocity = Vec3(0.0, 0.0, 0.0)
        else:
            self._Velocity = Vec3(0.0, self._Velocity.y, 0.0)

        if Input.is_key_pressed(Key.W):
            self._Velocity += self.transform.forward_vector * self.MovementSpeed * ts.get_seconds()
        elif Input.is_key_pressed(Key.S):
            self._Velocity -= self.transform.forward_vector * self.MovementSpeed * ts.get_seconds()

        if Input.is_key_pressed(Key.A):
            self._Velocity -= self.transform.right_vector * self.MovementSpeed * ts.get_seconds()
        elif Input.is_key_pressed(Key.D):
            self._Velocity += self.transform.right_vector * self.MovementSpeed * ts.get_seconds()

        if Input.is_key_pressed(Key.Space):
            if self._IsUnderWater:
                self._Velocity += self.transform.up_vector * self.MovementSpeed * ts.get_seconds()
            elif not self._IsInAir:
                self._Velocity += self.transform.up_vector * self.JumpForce * ts.get_seconds()
                self._IsInAir = True
        elif Input.is_key_pressed(Key.LShift):
            if self._IsUnderWater:
                self._Velocity -= self.transform.up_vector * self.MovementSpeed * ts.get_seconds()

        if not self._IsUnderWater:
            self._Velocity.y += self.GravityForce * ts.get_seconds()

        self.transform.translation += self._Velocity
        self.Camera.transform.translation = self.transform.translation

    def on_event(self, event: Event):
        if isinstance(event, MouseButtonPressedEvent):
            if event.mouse_button == MouseButton.Left:
                self.break_block()
            elif event.mouse_button == MouseButton.Right:
                self.place_block()

    def break_block(self) -> None:
        world: World = self.World.get_script()
        intersectedBlockCoords: list = Utils.ray_cast(self.transform.translation, self.Camera.transform.forward_vector, self.BlockBreakRange)
        for blockCoords in intersectedBlockCoords:
            blockType: BlockType = world.get_block_at_position(blockCoords)
            if blockType != BlockType.Air and blockType != BlockType.Water:
                replacementBlock: BlockType = BlockType.Air
                for i in range(-1, 2, 2):
                    if world.get_block_at_position(Vec3(blockCoords.x + i, blockCoords.y, blockCoords.z)) == BlockType.Water:
                        replacementBlock = BlockType.Water
                        break
                for i in range(-1, 2, 2):
                    if world.get_block_at_position(Vec3(blockCoords.x, blockCoords.y, blockCoords.z + i)) == BlockType.Water:
                        replacementBlock = BlockType.Water
                        break
                world.set_block_at_position(blockCoords, replacementBlock)
                break

    def place_block(self) -> None:
        world: World = self.World.get_script()
        intersectedBlockCoords: list = Utils.ray_cast(self.transform.translation, self.Camera.transform.forward_vector, self.BlockBreakRange)
        prevCoords: Vec3 = intersectedBlockCoords[0]
        for blockCoords in intersectedBlockCoords:
            blockType: BlockType = world.get_block_at_position(blockCoords)
            if blockType != BlockType.Air and blockType != BlockType.Water:
                if Math.distance(prevCoords, self.transform.translation) >= 1.8:
                    world.set_block_at_position(prevCoords, BlockType.Wood)
                break
            prevCoords = blockCoords
        