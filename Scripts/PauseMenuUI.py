from Atom import *
from GameConstants import *

class PauseMenuUI(Entity):
    pause_menu_size: Vec2
    close_button_size: float
    menu_button_size: Vec2
    inventory: Entity
    _is_opened: bool

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.pause_menu_size = Vec2(300.0, 300.0)
        self.close_button_size = 32.0
        self.menu_button_size = Vec2(250.0, 32.0)
        self.inventory = Entity(0)
        self._is_opened = False

    def on_gui(self) -> None:
        if self._is_opened:
            viewport_size: Vec2 = GUI.get_window_size()
            item_spacing: int = 4
            GUI.begin_child_window("Pause menu", self.pause_menu_size, Vec2(viewport_size.x / 2.0 - self.pause_menu_size.x / 2.0, viewport_size.y / 2.0 - self.pause_menu_size.y / 2.0))
            GUI.text("Pause menu", Vec2(item_spacing + 5.0, item_spacing))

            if GUI.button("X", Vec2(self.close_button_size, self.close_button_size), Vec2(GUI.get_window_size().x - self.close_button_size, 0)):
                self.toggle()

            if GUI.button("Return to game", self.menu_button_size, Vec2(GUI.get_window_size().x / 2.0 - self.menu_button_size.x / 2.0, self.close_button_size + item_spacing)):
                self.toggle()

            if GUI.button("Exit", self.menu_button_size, Vec2(GUI.get_window_size().x / 2.0 - self.menu_button_size.x / 2.0, self.close_button_size + self.menu_button_size.y + item_spacing * 2.0)):
                Application.close()

            GUI.end_child_window()

    def on_event(self, event: Event):
        if isinstance(event, KeyPressedEvent):
            if event.key == Key.Esc:
                if self.inventory.is_valid() and self.inventory.get_script().is_opened():
                    self.inventory.get_script().toggle()
                self.toggle()

    def is_opened(self) -> bool:
        return self._is_opened

    def toggle(self) -> None:
        self._is_opened = not self._is_opened
        Input.set_mouse_cursor(self._is_opened)