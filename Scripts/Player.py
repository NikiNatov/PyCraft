from Atom import *
from GameConstants import *
from Block import BlockType
from World import World
import Utils

class Player(Entity):
    jump_force: float
    movement_speed: float
    rotation_speed: float
    block_break_range: float
    bounding_box: Vec3
    camera_holder: Entity
    world: Entity
    camera_first_person: Entity
    camera_third_person: Entity
    inventory: Entity
    toolbar: Entity
    pause_menu: Entity
    _use_third_person_camera: bool
    _vertical_force: float
    _is_in_air: bool
    _velocity: Vec3
    _prev_mouse_pos: Vec2

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.jump_force = 5.0
        self.movement_speed = 7.0
        self.rotation_speed = 7.0
        self.block_break_range = 5.0
        self.bounding_box = Vec3(0.6, 1.8, 0.6)
        self.camera_holder = Entity(0)
        self.world = Entity(0)
        self.camera_first_person = Entity(0)
        self.camera_third_person = Entity(0)
        self.toolbar = Entity(0)
        self._use_third_person_camera = False
        self._vertical_force = 0.0
        self._is_in_air = True
        self._velocity = Vec3(0.0, 0.0, 0.0)
        self._prev_mouse_pos = Vec2(0.0, 0.0)

    def on_create(self) -> None:
        self._prev_mouse_pos = Input.get_mouse_position()
        Input.set_mouse_cursor(False)

    def on_update(self, ts: Timestep) -> None:
        if Input.is_cursor_enabled():
            return
        
        # Compute rotations
        current_mouse_pos: Vec2 = Input.get_mouse_position()
        mouse_delta: Vec2 = current_mouse_pos - self._prev_mouse_pos
        Input.set_mouse_position(self._prev_mouse_pos)
        
        self.camera_holder.transform.rotation.x -= Math.radians(mouse_delta.y * self.rotation_speed * ts.get_seconds())

        if self.camera_holder.transform.rotation.x > Math.radians(89.0):
            self.camera_holder.transform.rotation.x = Math.radians(89.0)
        elif self.camera_holder.transform.rotation.x < Math.radians(-89.0):
            self.camera_holder.transform.rotation.x = Math.radians(-89.0)

        self.transform.rotation.y -= Math.radians(mouse_delta.x * self.rotation_speed * ts.get_seconds())
        self.camera_holder.transform.rotation.y -= Math.radians(mouse_delta.x * self.rotation_speed * ts.get_seconds())

        # Compute directional movement
        if self._vertical_force > GRAVITY:
            self._vertical_force += GRAVITY * ts.get_seconds()

        self._velocity = Vec3(0.0, 0.0, 0.0)
        if Input.is_key_pressed(Key.W):
            self._velocity += self.transform.forward_vector * self.movement_speed * ts.get_seconds()
        elif Input.is_key_pressed(Key.S):
            self._velocity -= self.transform.forward_vector * self.movement_speed * ts.get_seconds()

        if Input.is_key_pressed(Key.A):
            self._velocity -= self.transform.right_vector * self.movement_speed * ts.get_seconds()
        elif Input.is_key_pressed(Key.D):
            self._velocity += self.transform.right_vector * self.movement_speed * ts.get_seconds()

        self._velocity += self.transform.up_vector * self._vertical_force * ts.get_seconds()

        if (self._velocity.x > 0.0 and self._check_collision_right()) or (self._velocity.x < 0.0 and self._check_collision_left()):
            self._velocity.x = 0.0
        if (self._velocity.z > 0.0 and self._check_collision_front()) or (self._velocity.z < 0.0 and self._check_collision_back()):
            self._velocity.z = 0.0

        if self._velocity.y < 0.0:
            if self._check_collision_down():
                self._is_in_air = False
                self._velocity.y = 0.0
            else:
                self._is_in_air = True
        elif self._velocity.y > 0.0:
            if self._check_collision_up():
                self._velocity.y = 0.0

        self.transform.translation += self._velocity
        self.camera_holder.transform.translation = self.transform.translation

    def on_event(self, event: Event) -> None:
        if isinstance(event, MouseButtonPressedEvent):
            if event.mouse_button == MouseButton.Left:
                if not Input.is_cursor_enabled():
                    self.break_block()
            elif event.mouse_button == MouseButton.Right:
                if not Input.is_cursor_enabled():
                    self.place_block()
        elif isinstance(event, KeyPressedEvent):
            if event.key == Key.Space:
                if not Input.is_cursor_enabled():
                    self.jump()
            elif event.key == Key.F2:
                if not Input.is_cursor_enabled():
                    self._use_third_person_camera = not self._use_third_person_camera
                    self.camera_first_person.get_camera_component().is_primary_camera = not self._use_third_person_camera
                    self.camera_third_person.get_camera_component().is_primary_camera = self._use_third_person_camera

    def jump(self) -> None:
        if not self._is_in_air:
            self._is_in_air = True
            self._vertical_force = self.jump_force

    def break_block(self) -> None:
        world: World = self.world.get_script()
        intersected_block_coords: list = Utils.ray_cast(self.transform.translation, self.camera_holder.transform.forward_vector, self.block_break_range)
        for block_coords in intersected_block_coords:
            block_type: BlockType = world.get_block_at_position(block_coords)
            if block_type != BlockType.Air and block_type != BlockType.Water:
                replacement_block: BlockType = BlockType.Air
                for i in range(-1, 2, 2):
                    if world.get_block_at_position(Vec3(block_coords.x + i, block_coords.y, block_coords.z)) == BlockType.Water:
                        replacement_block = BlockType.Water
                        break
                for i in range(-1, 2, 2):
                    if world.get_block_at_position(Vec3(block_coords.x, block_coords.y, block_coords.z + i)) == BlockType.Water:
                        replacement_block = BlockType.Water
                        break
                world.set_block_at_position(block_coords, replacement_block)
                break

    def place_block(self) -> None:
        world: World = self.world.get_script()
        intersected_block_coords: list = Utils.ray_cast(self.transform.translation, self.camera_holder.transform.forward_vector, self.block_break_range)
        prev_coords: Vec3 = intersected_block_coords[0]
        for block_coords in intersected_block_coords:
            block_type: BlockType = world.get_block_at_position(block_coords)
            if block_type != BlockType.Air and block_type != BlockType.Water:
                if Math.distance(prev_coords, self.transform.translation) >= 1.8:
                    world.set_block_at_position(prev_coords, self.toolbar.get_script().get_selected_slot_block())
                break
            prev_coords = block_coords
    
    def _check_collision_left(self) -> bool:
        player_pos: Vec3 = self.transform.translation
        world: World = self.world.get_script()
        return (world.is_block_solid(Vec3(player_pos.x - self.bounding_box.x / 2.0, player_pos.y - self.bounding_box.y * 0.80, player_pos.z)) or
                world.is_block_solid(Vec3(player_pos.x - self.bounding_box.x / 2.0, player_pos.y + self.bounding_box.y * 0.20, player_pos.z)))
    
    def _check_collision_right(self) -> bool:
        player_pos: Vec3 = self.transform.translation
        world: World = self.world.get_script()
        return (world.is_block_solid(Vec3(player_pos.x + self.bounding_box.x / 2.0, player_pos.y - self.bounding_box.y * 0.80, player_pos.z)) or
                world.is_block_solid(Vec3(player_pos.x + self.bounding_box.x / 2.0, player_pos.y + self.bounding_box.y * 0.20, player_pos.z)))
    
    def _check_collision_front(self) -> bool:
        player_pos: Vec3 = self.transform.translation
        world: World = self.world.get_script()
        return (world.is_block_solid(Vec3(player_pos.x, player_pos.y - self.bounding_box.y * 0.80, player_pos.z + self.bounding_box.z / 2.0)) or
                world.is_block_solid(Vec3(player_pos.x, player_pos.y + self.bounding_box.y * 0.20, player_pos.z + self.bounding_box.z / 2.0)))
    
    def _check_collision_back(self) -> bool:
        player_pos: Vec3 = self.transform.translation
        world: World = self.world.get_script()
        return (world.is_block_solid(Vec3(player_pos.x, player_pos.y - self.bounding_box.y * 0.80, player_pos.z - self.bounding_box.z / 2.0)) or
                world.is_block_solid(Vec3(player_pos.x, player_pos.y + self.bounding_box.y * 0.20, player_pos.z - self.bounding_box.z / 2.0)))
    
    def _check_collision_up(self) -> bool:
        player_pos: Vec3 = self.transform.translation
        world: World = self.world.get_script()
        # We have to make sure we are actually above above the block when we check the 4 corners otherwise we can get stuck in walls.
        # Checking for no collisions for all horizontal directions will make sure that the blocks next to us are non-solid
        collision_left: bool = self._check_collision_left()
        collision_right: bool = self._check_collision_right()
        collision_front: bool = self._check_collision_front()
        collision_back: bool = self._check_collision_back()
        return ((world.is_block_solid(Vec3(player_pos.x - self.bounding_box.x / 2.0, player_pos.y + self.bounding_box.y * 0.20 + self._velocity.y, player_pos.z - self.bounding_box.z / 2.0)) and not collision_left and not collision_back) or
                (world.is_block_solid(Vec3(player_pos.x + self.bounding_box.x / 2.0, player_pos.y + self.bounding_box.y * 0.20 + self._velocity.y, player_pos.z + self.bounding_box.z / 2.0)) and not collision_right and not collision_front) or
                (world.is_block_solid(Vec3(player_pos.x - self.bounding_box.x / 2.0, player_pos.y + self.bounding_box.y * 0.20 + self._velocity.y, player_pos.z + self.bounding_box.z / 2.0)) and not collision_left and not collision_front) or
                (world.is_block_solid(Vec3(player_pos.x + self.bounding_box.x / 2.0, player_pos.y + self.bounding_box.y * 0.20 + self._velocity.y, player_pos.z - self.bounding_box.z / 2.0)) and not collision_right and not collision_back))
    
    def _check_collision_down(self) -> bool:
        player_pos: Vec3 = self.transform.translation
        world: world = self.world.get_script()
        # We have to make sure we are actually above above the block when we check the 4 corners otherwise we can get stuck in walls.
        # Checking for no collisions for all horizontal directions will make sure that the blocks next to us are non-solid
        collision_left: bool = self._check_collision_left()
        collision_right: bool = self._check_collision_right()
        collision_front: bool = self._check_collision_front()
        collision_back: bool = self._check_collision_back()
        return ((world.is_block_solid(Vec3(player_pos.x - self.bounding_box.x / 2.0, player_pos.y - self.bounding_box.y * 0.80 + self._velocity.y, player_pos.z - self.bounding_box.z / 2.0)) and not collision_left and not collision_back) or
                (world.is_block_solid(Vec3(player_pos.x + self.bounding_box.x / 2.0, player_pos.y - self.bounding_box.y * 0.80 + self._velocity.y, player_pos.z + self.bounding_box.z / 2.0)) and not collision_right and not collision_front) or
                (world.is_block_solid(Vec3(player_pos.x - self.bounding_box.x / 2.0, player_pos.y - self.bounding_box.y * 0.80 + self._velocity.y, player_pos.z + self.bounding_box.z / 2.0)) and not collision_left and not collision_front) or
                (world.is_block_solid(Vec3(player_pos.x + self.bounding_box.x / 2.0, player_pos.y - self.bounding_box.y * 0.80 + self._velocity.y, player_pos.z - self.bounding_box.z / 2.0)) and not collision_right and not collision_back))