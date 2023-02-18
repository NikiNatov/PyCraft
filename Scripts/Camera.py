from Atom import *

class Camera(Entity):
    RotationSpeed: float
    Player: Entity
    _PrevMousePos: Vec2

    def __init__(self, entityID: int):
        super().__init__(entityID)
        self.RotationSpeed = 7.0
        self.Player = Entity(0)
        self._PrevMousePos = Vec2(0.0, 0.0)

    def on_create(self) -> None:
        self._PrevMousePos = Input.get_mouse_position()
        Input.set_mouse_cursor(False)

    def on_update(self, ts: Timestep) -> None:
        if self.Player.is_valid():
            if Input.is_cursor_enabled():
                return
            
            currentMousePos: Vec2 = Input.get_mouse_position()
            mouseDelta: Vec2 = currentMousePos - self._PrevMousePos

            Input.set_mouse_position(self._PrevMousePos)

            self.transform.rotation.x -= Math.radians(mouseDelta.y * self.RotationSpeed * ts.get_seconds())
            self.transform.rotation.y -= Math.radians(mouseDelta.x * self.RotationSpeed * ts.get_seconds())
            self.Player.transform.rotation.y = self.transform.rotation.y

            if self.transform.rotation.x > Math.radians(89.0):
                self.transform.rotation.x = Math.radians(89.0)
            elif self.transform.rotation.x < Math.radians(-89.0):
                self.transform.rotation.x = Math.radians(-89.0)
