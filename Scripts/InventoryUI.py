from Atom import *
from Block import *
from GameConstants import *

class InventoryUI(Entity):
    BlockIconsTexture: Texture2D
    InventorySize: Vec2
    CloseButtonSize: float
    SlotSize: float
    Rows: int
    Columns: int
    _IsOpened: bool
    _ItemSlots: list

    def __init__(self, entityID: int) -> None:
        super().__init__(entityID)
        self.BlockIconsTexture = Texture2D(0)
        self.InventorySize = Vec2(300.0, 300.0)
        self.CloseButtonSize = 32.0
        self.SlotSize = 40.0
        self.Rows = 7
        self.Columns = 7
        self._IsOpened = False
        self._ItemSlots = []

    def on_create(self) -> None:
        self._ItemSlots = [None] * self.Rows * self.Columns
        for index, blockType in enumerate(BLOCK_TYPES):
            self._ItemSlots[index] = blockType

    def on_gui(self) -> None:
        if self._IsOpened:
            viewportSize: Vec2 = GUI.get_window_size()
            itemSpacing: int = 4
            GUI.begin_child_window("Inventory", self.InventorySize, Vec2(viewportSize.x / 2.0 - self.InventorySize.x / 2.0, viewportSize.y / 2.0 - self.InventorySize.y / 2.0))
            GUI.text("Inventory", Vec2(itemSpacing + 5.0, itemSpacing))
            if GUI.button("X", Vec2(self.CloseButtonSize, self.CloseButtonSize), Vec2(GUI.get_window_size().x - self.CloseButtonSize, 0)):
                self._IsOpened = False

            for j in range(self.Rows):
                for i in range(int(-self.Columns / 2.0), int(self.Columns / 2.0) + 1):
                    slotPosition: Vec2 = Vec2(0.0, 0.0)
                    slotIdx: int = 0
                    if self.Columns % 2 != 0:
                        slotIdx: int = j * self.Columns + (i + int(self.Columns / 2.0))
                        slotPosition.x = (self.SlotSize + itemSpacing) * i + GUI.get_window_size().x / 2.0 - self.SlotSize / 2.0
                        slotPosition.y = (self.SlotSize + itemSpacing) * j + (self.CloseButtonSize + itemSpacing + 10.0)
                    else:
                        if i == 0:
                            continue
                        slotIdx: int = j * self.Columns + (i + int(self.Columns / 2.0)) - int(i > 0)
                        slotPosition.x = (self.SlotSize + itemSpacing) * (i - int(i > 0)) + GUI.get_window_size().x / 2.0
                        slotPosition.y = (self.SlotSize + itemSpacing) * j + (self.CloseButtonSize + itemSpacing + 10.0)
                    
                    if(self._ItemSlots[slotIdx] is None or self._ItemSlots[slotIdx] == BlockType.Air):
                        GUI.image(Texture2D(0), Vec2(self.SlotSize, self.SlotSize), Vec2(0.0, 0.0), Vec2(1.0, 1.0), slotPosition)
                    else:
                        uvs: list = BLOCK_TYPES[self._ItemSlots[slotIdx]].calculate_uvs(BlockFace.FrontFace)
                        GUI.image(self.BlockIconsTexture, Vec2(self.SlotSize, self.SlotSize), Vec2(uvs[0][0], uvs[0][1]), Vec2(uvs[3][0], uvs[3][1]), slotPosition)
                        if GUI.begin_drag_drop_source():
                            GUI.set_drag_drop_payload("ItemSlot", self._ItemSlots[slotIdx])
                            GUI.image(self.BlockIconsTexture, Vec2(self.SlotSize, self.SlotSize), Vec2(uvs[0][0], uvs[0][1]), Vec2(uvs[3][0], uvs[3][1]))
                            GUI.end_drag_drop_source()

            GUI.end_child_window()

    def toggle(self) -> None:
        self._IsOpened = not self._IsOpened