from Atom import *
from GameConstants import *
from Block import BlockFace, BlockType, BLOCK_TYPES

class InventoryUI(Entity):
    block_icons_texture: Texture2D
    inventory_size: Vec2
    close_button_size: float
    slot_size: float
    rows: int
    columns: int
    pause_menu: Entity
    _is_opened: bool
    _item_slots: list

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.block_icons_texture = Texture2D(0)
        self.inventory_size = Vec2(300.0, 300.0)
        self.close_button_size = 32.0
        self.slot_size = 40.0
        self.rows = 7
        self.columns = 7
        self.pause_menu = Entity(0)
        self._is_opened = False
        self._item_slots = []

    def on_create(self) -> None:
        self._item_slots = [None] * self.rows * self.columns
        for index, block_type in enumerate(BLOCK_TYPES):
            self._item_slots[index] = block_type

    def on_gui(self) -> None:
        if self._is_opened:
            viewport_size: Vec2 = GUI.get_window_size()
            item_spacing: int = 4
            GUI.begin_child_window("Inventory", self.inventory_size, Vec2(viewport_size.x / 2.0 - self.inventory_size.x / 2.0, viewport_size.y / 2.0 - self.inventory_size.y / 2.0))
            GUI.text("Inventory", Vec2(item_spacing + 5.0, item_spacing))

            if GUI.button("X", Vec2(self.close_button_size, self.close_button_size), Vec2(GUI.get_window_size().x - self.close_button_size, 0)):
                self.toggle()

            for j in range(self.rows):
                for i in range(int(-self.columns / 2.0), int(self.columns / 2.0) + 1):
                    slot_position: Vec2 = Vec2(0.0, 0.0)
                    slot_idx: int = 0
                    if self.columns % 2 != 0:
                        slot_idx: int = j * self.columns + (i + int(self.columns / 2.0))
                        slot_position.x = (self.slot_size + item_spacing) * i + GUI.get_window_size().x / 2.0 - self.slot_size / 2.0
                        slot_position.y = (self.slot_size + item_spacing) * j + (self.close_button_size + item_spacing + 10.0)
                    else:
                        if i == 0:
                            continue
                        slot_idx: int = j * self.columns + (i + int(self.columns / 2.0)) - int(i > 0)
                        slot_position.x = (self.slot_size + item_spacing) * (i - int(i > 0)) + GUI.get_window_size().x / 2.0
                        slot_position.y = (self.slot_size + item_spacing) * j + (self.close_button_size + item_spacing + 10.0)
                    
                    if(self._item_slots[slot_idx] is None or self._item_slots[slot_idx] == BlockType.Air):
                        GUI.image(Texture2D(0), Vec2(self.slot_size, self.slot_size), Vec2(0.0, 0.0), Vec2(1.0, 1.0), slot_position)
                    else:
                        uvs: list = BLOCK_TYPES[self._item_slots[slot_idx]].calculate_uvs(BlockFace.FrontFace)
                        GUI.image(self.block_icons_texture, Vec2(self.slot_size, self.slot_size), Vec2(uvs[0][0], uvs[0][1]), Vec2(uvs[3][0], uvs[3][1]), slot_position)
                        if GUI.begin_drag_drop_source():
                            GUI.set_drag_drop_payload("ItemSlot", self._item_slots[slot_idx])
                            GUI.image(self.block_icons_texture, Vec2(self.slot_size, self.slot_size), Vec2(uvs[0][0], uvs[0][1]), Vec2(uvs[3][0], uvs[3][1]))
                            GUI.end_drag_drop_source()

            GUI.end_child_window()

    def on_event(self, event: Event):
        if isinstance(event, KeyPressedEvent):
            if event.key == Key.I:
                if self.pause_menu.is_valid() and self.pause_menu.get_script().is_opened():
                    self.pause_menu.get_script().toggle()
                self.toggle()

    def is_opened(self) -> bool:
        return self._is_opened

    def toggle(self) -> None:
        self._is_opened = not self._is_opened
        Input.set_mouse_cursor(self._is_opened)