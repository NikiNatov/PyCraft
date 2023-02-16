from Atom import *
from Block import *
from ChunkDataManager import *
from Chunk import *
from World import *
from GameConstants import *

import Utils

class Player(Entity):
    JumpForce: float
    MovementSpeed: float
    BlockBreakRange: float
    BoundingBox: Vec3
    World: Entity
    Camera: Entity
    Inventory: Entity
    Toolbar: Entity
    _VerticalForce: float
    _IsInAir: bool
    _PrevMousePos: Vec2
    _Velocity: Vec3

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.JumpForce = 5.0
        self.MovementSpeed = 7.0
        self.BlockBreakRange = 5.0
        self.BoundingBox = Vec3(0.6, 1.8, 0.6)
        self.World = Entity(0)
        self.Camera = Entity(0)
        self.Inventory = Entity(0)
        self.Toolbar = Entity(0)
        self._VerticalForce = 0.0
        self._IsInAir = True
        self._Velocity = Vec3(0.0, 0.0, 0.0)

    def on_create(self) -> None:
        pass

    def on_update(self, ts: Timestep) -> None:
        if self._VerticalForce > GRAVITY:
            self._VerticalForce += GRAVITY * ts.get_seconds()

        self._Velocity = Vec3(0.0, 0.0, 0.0)

        if Input.is_key_pressed(Key.W):
            self._Velocity += self.transform.forward_vector * self.MovementSpeed * ts.get_seconds()
        elif Input.is_key_pressed(Key.S):
            self._Velocity -= self.transform.forward_vector * self.MovementSpeed * ts.get_seconds()

        if Input.is_key_pressed(Key.A):
            self._Velocity -= self.transform.right_vector * self.MovementSpeed * ts.get_seconds()
        elif Input.is_key_pressed(Key.D):
            self._Velocity += self.transform.right_vector * self.MovementSpeed * ts.get_seconds()

        self._Velocity += self.transform.up_vector * self._VerticalForce * ts.get_seconds()

        if (self._Velocity.x > 0.0 and self._check_collision_right()) or (self._Velocity.x < 0.0 and self._check_collision_left()):
            self._Velocity.x = 0.0
        if (self._Velocity.z > 0.0 and self._check_collision_front()) or (self._Velocity.z < 0.0 and self._check_collision_back()):
            self._Velocity.z = 0.0

        if self._Velocity.y < 0.0:
            if self._check_collision_down():
                self._IsInAir = False
                self._Velocity.y = 0.0
            else:
                self._IsInAir = True
        elif self._Velocity.y > 0.0:
            if self._check_collision_up():
                self._Velocity.y = 0.0

        self.transform.translation += self._Velocity
        self.Camera.transform.translation = self.transform.translation

    def on_event(self, event: Event):
        if isinstance(event, MouseButtonPressedEvent):
            if event.mouse_button == MouseButton.Left:
                self.break_block()
            elif event.mouse_button == MouseButton.Right:
                self.place_block()
        elif isinstance(event, KeyPressedEvent):
            if event.key == Key.Space:
                self.jump()
            elif event.key == Key.I:
                if self.Inventory.is_valid():
                    self.Inventory.get_script().toggle()
                    Input.set_mouse_cursor(True)
            elif event.key == Key.Key1:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(0)
            elif event.key == Key.Key2:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(1)
            elif event.key == Key.Key3:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(2)
            elif event.key == Key.Key4:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(3)
            elif event.key == Key.Key5:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(4)
            elif event.key == Key.Key6:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(5)
            elif event.key == Key.Key7:
                if self.Toolbar.is_valid():
                    self.Toolbar.get_script().set_selected_slot(6)

    def jump(self) -> None:
        if not self._IsInAir:
            self._IsInAir = True
            self._VerticalForce = self.JumpForce

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
                    world.set_block_at_position(prevCoords, self.Toolbar.get_script().get_selected_slot_block())
                break
            prevCoords = blockCoords
    
    def _check_collision_left(self) -> bool:
        playerPos: Vec3 = self.transform.translation
        world: World = self.World.get_script()
        return (world.is_block_solid(Vec3(playerPos.x - self.BoundingBox.x / 2.0, playerPos.y - self.BoundingBox.y * 0.80, playerPos.z)) or
                world.is_block_solid(Vec3(playerPos.x - self.BoundingBox.x / 2.0, playerPos.y + self.BoundingBox.y * 0.20, playerPos.z)))
    
    def _check_collision_right(self) -> bool:
        playerPos: Vec3 = self.transform.translation
        world: World = self.World.get_script()
        return (world.is_block_solid(Vec3(playerPos.x + self.BoundingBox.x / 2.0, playerPos.y - self.BoundingBox.y * 0.80, playerPos.z)) or
                world.is_block_solid(Vec3(playerPos.x + self.BoundingBox.x / 2.0, playerPos.y + self.BoundingBox.y * 0.20, playerPos.z)))
    
    def _check_collision_front(self) -> bool:
        playerPos: Vec3 = self.transform.translation
        world: World = self.World.get_script()
        return (world.is_block_solid(Vec3(playerPos.x, playerPos.y - self.BoundingBox.y * 0.80, playerPos.z + self.BoundingBox.z / 2.0)) or
                world.is_block_solid(Vec3(playerPos.x, playerPos.y + self.BoundingBox.y * 0.20, playerPos.z + self.BoundingBox.z / 2.0)))
    
    def _check_collision_back(self) -> bool:
        playerPos: Vec3 = self.transform.translation
        world: World = self.World.get_script()
        return (world.is_block_solid(Vec3(playerPos.x, playerPos.y - self.BoundingBox.y * 0.80, playerPos.z - self.BoundingBox.z / 2.0)) or
                world.is_block_solid(Vec3(playerPos.x, playerPos.y + self.BoundingBox.y * 0.20, playerPos.z - self.BoundingBox.z / 2.0)))
    
    def _check_collision_up(self) -> bool:
        playerPos: Vec3 = self.transform.translation
        world: World = self.World.get_script()
        # We have to make sure we are actually above above the block when we check the 4 corners otherwise we can get stuck in walls.
        # Checking for no collisions for all horizontal directions will make sure that the blocks next to us are non-solid
        collisionLeft: bool = self._check_collision_left()
        collisionRight: bool = self._check_collision_right()
        collisionFront: bool = self._check_collision_front()
        collisionBack: bool = self._check_collision_back()
        return ((world.is_block_solid(Vec3(playerPos.x - self.BoundingBox.x / 2.0, playerPos.y + self.BoundingBox.y * 0.20 + self._Velocity.y, playerPos.z - self.BoundingBox.z / 2.0)) and not collisionLeft and not collisionBack) or
                (world.is_block_solid(Vec3(playerPos.x + self.BoundingBox.x / 2.0, playerPos.y + self.BoundingBox.y * 0.20 + self._Velocity.y, playerPos.z + self.BoundingBox.z / 2.0)) and not collisionRight and not collisionFront) or
                (world.is_block_solid(Vec3(playerPos.x - self.BoundingBox.x / 2.0, playerPos.y + self.BoundingBox.y * 0.20 + self._Velocity.y, playerPos.z + self.BoundingBox.z / 2.0)) and not collisionLeft and not collisionFront) or
                (world.is_block_solid(Vec3(playerPos.x + self.BoundingBox.x / 2.0, playerPos.y + self.BoundingBox.y * 0.20 + self._Velocity.y, playerPos.z - self.BoundingBox.z / 2.0)) and not collisionRight and not collisionBack))
    
    def _check_collision_down(self) -> bool:
        playerPos: Vec3 = self.transform.translation
        world: World = self.World.get_script()
        # We have to make sure we are actually above above the block when we check the 4 corners otherwise we can get stuck in walls.
        # Checking for no collisions for all horizontal directions will make sure that the blocks next to us are non-solid
        collisionLeft: bool = self._check_collision_left()
        collisionRight: bool = self._check_collision_right()
        collisionFront: bool = self._check_collision_front()
        collisionBack: bool = self._check_collision_back()
        return ((world.is_block_solid(Vec3(playerPos.x - self.BoundingBox.x / 2.0, playerPos.y - self.BoundingBox.y * 0.80 + self._Velocity.y, playerPos.z - self.BoundingBox.z / 2.0)) and not collisionLeft and not collisionBack) or
                (world.is_block_solid(Vec3(playerPos.x + self.BoundingBox.x / 2.0, playerPos.y - self.BoundingBox.y * 0.80 + self._Velocity.y, playerPos.z + self.BoundingBox.z / 2.0)) and not collisionRight and not collisionFront) or
                (world.is_block_solid(Vec3(playerPos.x - self.BoundingBox.x / 2.0, playerPos.y - self.BoundingBox.y * 0.80 + self._Velocity.y, playerPos.z + self.BoundingBox.z / 2.0)) and not collisionLeft and not collisionFront) or
                (world.is_block_solid(Vec3(playerPos.x + self.BoundingBox.x / 2.0, playerPos.y - self.BoundingBox.y * 0.80 + self._Velocity.y, playerPos.z - self.BoundingBox.z / 2.0)) and not collisionRight and not collisionBack))