from Atom import *
from Block import BlockType, BlockFace, BLOCK_TYPES

class ToolbarUI(Entity):
    block_icons_texture: Texture2D
    slot_count: int
    slot_size: float
    _selected_slot: int
    _item_slots: list

    def __init__(self, entity_id: int) -> None:
        super().__init__(entity_id)
        self.block_icons_texture = Texture2D(0)
        self.slot_count = 7
        self.slot_size = 64.0
        self._selected_slot = 0
        self._item_slots = []

    def on_create(self) -> None:
        self._item_slots = [None] * self.slot_count
        for index, block_type in enumerate(BLOCK_TYPES):
            if index >= len(self._item_slots):
                break
            self._item_slots[index] = block_type

    def on_gui(self) -> None:
        window_size: Vec2 = GUI.get_window_size()
        item_spacing: int = 4
        for i in range(int(-self.slot_count / 2.0), int(self.slot_count / 2.0) + 1):
            slot_position: Vec2 = Vec2(0.0, window_size.y - 100.0)
            slot_idx: int = 0
            if self.slot_count % 2 != 0:
                slot_idx: int = i + int(self.slot_count / 2.0)
                slot_position.x = (self.slot_size + item_spacing) * i + window_size.x / 2.0 - self.slot_size / 2.0
            else:
                if i == 0:
                    continue
                slot_idx: int = (i + int(self.slot_count / 2.0)) - int(i > 0)
                slot_position.x = (self.slot_size + item_spacing) * (i - int(i > 0)) + window_size.x / 2.0
            
            if(self._item_slots[slot_idx] is None or self._item_slots[slot_idx] == BlockType.Air):
                GUI.image_button(Texture2D(0), Vec2(self.slot_size, self.slot_size), Vec2(0.0, 0.0), Vec2(1.0, 1.0), slot_position)
                if GUI.begin_drag_drop_target():
                    block_type: BlockType = GUI.get_drag_drop_payload("ItemSlot")
                    if block_type is not None:
                        self._item_slots[slot_idx] = block_type
                    GUI.end_drag_drop_target()
            else:
                uvs: list = BLOCK_TYPES[self._item_slots[slot_idx]].calculate_uvs(BlockFace.FrontFace)
                GUI.image(self.block_icons_texture, Vec2(self.slot_size, self.slot_size), Vec2(uvs[0][0], uvs[0][1]), Vec2(uvs[3][0], uvs[3][1]), slot_position)
                if GUI.begin_drag_drop_target():
                    block_type: BlockType = GUI.get_drag_drop_payload("ItemSlot")
                    if block_type is not None:
                        self._item_slots[slot_idx] = block_type
                    GUI.end_drag_drop_target()

    def on_event(self, event: Event):
        if isinstance(event, KeyPressedEvent):
            if event.key == Key.Key1:
                self.set_selected_slot(0)
            elif event.key == Key.Key2:
                self.set_selected_slot(1)
            elif event.key == Key.Key3:
                self.set_selected_slot(2)
            elif event.key == Key.Key4:
                self.set_selected_slot(3)
            elif event.key == Key.Key5:
                self.set_selected_slot(4)
            elif event.key == Key.Key6:
                self.set_selected_slot(5)
            elif event.key == Key.Key7:
                self.set_selected_slot(6)

    def set_selected_slot(self, slot_idx: int) -> None:
        self._selected_slot = slot_idx if slot_idx < len(self._item_slots) else 0

    def get_selected_slot_block(self) -> BlockType:
        return self._item_slots[self._selected_slot]