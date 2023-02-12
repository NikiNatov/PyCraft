from Atom import *

class CrosshairUI(Entity):
    CrosshairSize: Vec2
    CrosshairImage: Texture2D

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.CrosshairSize = Vec2(32.0, 32.0)
        self.CrosshairImage = Texture2D(0)

    def on_gui(self) -> None:
        windowSize: Vec2 = GUI.get_window_size()
        GUI.image(self.CrosshairImage, self.CrosshairSize, Vec2(0.0, 0.0), Vec2(1.0, 1.0), Vec2(windowSize.x / 2.0 - self.CrosshairSize.x / 2.0, windowSize.y / 2.0 - self.CrosshairSize.y / 2.0))