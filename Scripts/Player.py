from Atom import *

class Player(Entity):
    JumpForce: float
    GravityForce: float
    MovementSpeed: float
    World: Entity
    _IsInAir: bool
    _IsUnderWater: bool
    _PrevMousePos: Vec2
    _Velocity: Vec3

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.JumpForce = 10.0
        self.GravityForce = -20.0
        self.MovementSpeed = 7.0
        self.World = Entity(0)
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
        