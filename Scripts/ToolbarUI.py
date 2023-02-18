from Atom import *
from Block import *

class ToolbarUI(Entity):
    BlockIconsTexture: Texture2D
    SlotCount: int
    SlotSize: float
    _SelectedSlot: int
    _ItemSlots: list

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.BlockIconsTexture = Texture2D(0)
        self.SlotCount = 7
        self.SlotSize = 64.0
        self._SelectedSlot = 0
        self._ItemSlots = []

    def on_create(self) -> None:
        self._ItemSlots = [None] * self.SlotCount
        for index, blockType in enumerate(BLOCK_TYPES):
            if index >= len(self._ItemSlots):
                break
            self._ItemSlots[index] = blockType

    def on_gui(self) -> None:
        windowSize: Vec2 = GUI.get_window_size()
        itemSpacing: int = 4
        for i in range(int(-self.SlotCount / 2.0), int(self.SlotCount / 2.0) + 1):
            slotPosition: Vec2 = Vec2(0.0, windowSize.y - 100.0)
            slotIdx: int = 0
            if self.SlotCount % 2 != 0:
                slotIdx: int = i + int(self.SlotCount / 2.0)
                slotPosition.x = (self.SlotSize + itemSpacing) * i + windowSize.x / 2.0 - self.SlotSize / 2.0
            else:
                if i == 0:
                    continue
                slotIdx: int = (i + int(self.SlotCount / 2.0)) - int(i > 0)
                slotPosition.x = (self.SlotSize + itemSpacing) * (i - int(i > 0)) + windowSize.x / 2.0
            
            if(self._ItemSlots[slotIdx] is None or self._ItemSlots[slotIdx] == BlockType.Air):
                GUI.image_button(Texture2D(0), Vec2(self.SlotSize, self.SlotSize), Vec2(0.0, 0.0), Vec2(1.0, 1.0), slotPosition)
                if GUI.begin_drag_drop_target():
                    blockType: BlockType = GUI.get_drag_drop_payload("ItemSlot")
                    if blockType is not None:
                        self._ItemSlots[slotIdx] = blockType
                    GUI.end_drag_drop_target()
            else:
                uvs: list = BLOCK_TYPES[self._ItemSlots[slotIdx]].calculate_uvs(BlockFace.FrontFace)
                GUI.image(self.BlockIconsTexture, Vec2(self.SlotSize, self.SlotSize), Vec2(uvs[0][0], uvs[0][1]), Vec2(uvs[3][0], uvs[3][1]), slotPosition)
                if GUI.begin_drag_drop_target():
                    blockType: BlockType = GUI.get_drag_drop_payload("ItemSlot")
                    if blockType is not None:
                        self._ItemSlots[slotIdx] = blockType
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

    def set_selected_slot(self, slotIdx: int) -> None:
        self._SelectedSlot = slotIdx if slotIdx < len(self._ItemSlots) else 0

    def get_selected_slot_block(self) -> BlockType:
        return self._ItemSlots[self._SelectedSlot]