from Atom import *

class StatsUI(Entity):
    player: Entity

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.player = Entity(0)

    def on_gui(self) -> None:
        item_spacing: int = 4
        GUI.text("PyCraft Version 1.0", Vec2(item_spacing + 5.0, item_spacing))
        GUI.text(f"FPS: {Application.get_fps()}", Vec2(item_spacing + 5.0, item_spacing + 20.0))
        GUI.text(f"X: {int(self.player.transform.translation.x)}, Y: {int(self.player.transform.translation.y)}, Z: {int(self.player.transform.translation.z)}", Vec2(item_spacing + 5.0, item_spacing + 40.0))