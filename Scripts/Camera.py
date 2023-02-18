from Atom import *

class Camera(Entity):
    rotation_speed: float
    player: Entity
    _prev_mouse_pos: Vec2

    def __init__(self, entity_id: int):
        super().__init__(entity_id)
        self.rotation_speed = 7.0
        self.player = Entity(0)
        self._prev_mouse_pos = Vec2(0.0, 0.0)

    def on_create(self) -> None:
        self._prev_mouse_pos = Input.get_mouse_position()
        Input.set_mouse_cursor(False)

    def on_update(self, ts: Timestep) -> None:
        if self.player.is_valid():
            if Input.is_cursor_enabled():
                return
            
            current_mouse_pos: Vec2 = Input.get_mouse_position()
            mouse_delta: Vec2 = current_mouse_pos - self._prev_mouse_pos

            Input.set_mouse_position(self._prev_mouse_pos)

            self.transform.rotation.x -= Math.radians(mouse_delta.y * self.rotation_speed * ts.get_seconds())
            self.transform.rotation.y -= Math.radians(mouse_delta.x * self.rotation_speed * ts.get_seconds())
            self.player.transform.rotation.y = self.transform.rotation.y

            if self.transform.rotation.x > Math.radians(89.0):
                self.transform.rotation.x = Math.radians(89.0)
            elif self.transform.rotation.x < Math.radians(-89.0):
                self.transform.rotation.x = Math.radians(-89.0)
