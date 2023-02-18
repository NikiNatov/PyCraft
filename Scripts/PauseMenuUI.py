from Atom import *
from GameConstants import *

class PauseMenuUI(Entity):
    PauseMenuSize: Vec2
    CloseButtonSize: float
    MenuButtonSize: Vec2
    Inventory: Entity
    _IsOpened: bool

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.PauseMenuSize = Vec2(300.0, 300.0)
        self.CloseButtonSize = 32.0
        self.MenuButtonSize = Vec2(250.0, 32.0)
        self.Inventory = Entity(0)
        self._IsOpened = False

    def on_gui(self) -> None:
        if self._IsOpened:
            viewportSize: Vec2 = GUI.get_window_size()
            itemSpacing: int = 4
            GUI.begin_child_window("Pause menu", self.PauseMenuSize, Vec2(viewportSize.x / 2.0 - self.PauseMenuSize.x / 2.0, viewportSize.y / 2.0 - self.PauseMenuSize.y / 2.0))
            GUI.text("Pause menu", Vec2(itemSpacing + 5.0, itemSpacing))

            if GUI.button("X", Vec2(self.CloseButtonSize, self.CloseButtonSize), Vec2(GUI.get_window_size().x - self.CloseButtonSize, 0)):
                self.toggle()

            if GUI.button("Return to game", self.MenuButtonSize, Vec2(GUI.get_window_size().x / 2.0 - self.MenuButtonSize.x / 2.0, self.CloseButtonSize + itemSpacing)):
                self.toggle()

            if GUI.button("Exit", self.MenuButtonSize, Vec2(GUI.get_window_size().x / 2.0 - self.MenuButtonSize.x / 2.0, self.CloseButtonSize + self.MenuButtonSize.y + itemSpacing * 2.0)):
                Application.close()

            GUI.end_child_window()

    def on_event(self, event: Event):
        if isinstance(event, KeyPressedEvent):
            if event.key == Key.Esc:
                if self.Inventory.is_valid() and self.Inventory.get_script().is_opened():
                    self.Inventory.get_script().toggle()
                self.toggle()

    def is_opened(self) -> bool:
        return self._IsOpened

    def toggle(self) -> None:
        self._IsOpened = not self._IsOpened
        Input.set_mouse_cursor(self._IsOpened)