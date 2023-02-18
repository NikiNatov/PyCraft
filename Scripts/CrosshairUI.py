from Atom import *

class CrosshairUI(Entity):
    crosshair_size: Vec2
    crosshair_image: Texture2D

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.crosshair_size = Vec2(32.0, 32.0)
        self.crosshair_image = Texture2D(0)

    def on_gui(self) -> None:
        window_size: Vec2 = GUI.get_window_size()
        GUI.image(self.crosshair_image, self.crosshair_size, Vec2(0.0, 0.0), Vec2(1.0, 1.0), Vec2(window_size.x / 2.0 - self.crosshair_size.x / 2.0, window_size.y / 2.0 - self.crosshair_size.y / 2.0))