from Atom import * 
from GameConstants import *
from ChunkDataManager import ChunkData
from Block import BlockType

class Chunk:
    grid_position: tuple
    world: Entity
    _block_map: list
    _chunk_entity : Entity
    _mesh_component: MeshComponent

    def __init__(self, grid_position: tuple, world: Entity) -> None:
        self.grid_position = grid_position
        self.world = world
        self._block_map = [[[BlockType.Air for _ in range(CHUNK_WIDTH)] for _ in range(CHUNK_HEIGHT)] for _ in range(CHUNK_WIDTH)]
        self._chunk_entity = Entity.create_entity("Chunk {},{}".format(self.grid_position[0], self.grid_position[1]))
        self._chunk_entity.transform.translation = Vec3(self.grid_position[0] * CHUNK_WIDTH, 0.0, self.grid_position[1] * CHUNK_WIDTH)
        self._mesh_component = self._chunk_entity.add_mesh_component()

    def __del__(self) -> None:
        Entity.delete_entity(self._chunk_entity)

    def on_create(self) -> None:
        self._chunk_entity = Entity.create_entity("Chunk {},{}".format(self.grid_position[0], self.grid_position[1]))
        self._chunk_entity.transform.translation = Vec3(self.grid_position[0] * CHUNK_WIDTH, 0.0, self.grid_position[1] * CHUNK_WIDTH)
        self._mesh_component = self._chunk_entity.add_mesh_component()

    def update_data(self, chunk_data: ChunkData) -> None:
        # Init the block map
        if len(chunk_data.block_map) > 0:
            self._block_map = chunk_data.block_map

        # Create index array
        indices: list = []
        indices.extend(chunk_data.mesh.solid_indices)
        indices.extend(chunk_data.mesh.transparent_indices)
        indices.extend(chunk_data.mesh.water_indices)

        # Create submeshes
        submeshes: list = []
        current_idx_count: int = 0
        vertex_count: int = len(chunk_data.mesh.positions)
        solid_submesh: Submesh = Submesh()
        solid_submesh.start_vertex = 0
        solid_submesh.vertex_count = vertex_count
        solid_submesh.start_index = current_idx_count
        solid_submesh.index_count = len(chunk_data.mesh.solid_indices)
        solid_submesh.material_index = 0
        submeshes.append(solid_submesh)
        current_idx_count += len(chunk_data.mesh.solid_indices)

        if len(chunk_data.mesh.transparent_indices) > 0:
            transparent_submesh: Submesh = Submesh()
            transparent_submesh.start_vertex = 0
            transparent_submesh.vertex_count = vertex_count
            transparent_submesh.start_index = current_idx_count
            transparent_submesh.index_count = len(chunk_data.mesh.transparent_indices)
            transparent_submesh.material_index = len(submeshes)
            submeshes.append(transparent_submesh)
            current_idx_count += len(chunk_data.mesh.transparent_indices)

        if len(chunk_data.mesh.water_indices) > 0:
            water_submesh: Submesh = Submesh()
            water_submesh.start_vertex = 0
            water_submesh.vertex_count = vertex_count
            water_submesh.start_index = current_idx_count
            water_submesh.index_count = len(chunk_data.mesh.water_indices)
            water_submesh.material_index = len(submeshes)
            submeshes.append(water_submesh)
            current_idx_count += len(chunk_data.mesh.water_indices)

        self._mesh_component.mesh = Mesh()
        self._mesh_component.mesh.set_positions(chunk_data.mesh.positions)
        self._mesh_component.mesh.set_uvs(chunk_data.mesh.uvs)
        self._mesh_component.mesh.set_normals(chunk_data.mesh.normals)
        self._mesh_component.mesh.set_tangents(chunk_data.mesh.tangents)
        self._mesh_component.mesh.set_bitangents(chunk_data.mesh.bitangents)
        self._mesh_component.mesh.set_indices(indices)
        self._mesh_component.mesh.set_submeshes(submeshes)
        self._mesh_component.mesh.set_material(0, self.world.block_solid_material)
        if len(submeshes) > 1:
            self._mesh_component.mesh.set_material(1, self.world.block_transparent_material)
        if len(submeshes) > 2:
            self._mesh_component.mesh.set_material(2, self.world.block_transparent_material)
        self._mesh_component.mesh.update_gpu_data(True)

    def set_block(self, x: int, y: int, z: int, block_type: BlockType) -> None:
        if self._is_block_in_chunk(x, y, z):
            self._block_map[x][y][z] = block_type

    def get_block(self, x: int, y: int, z: int) -> BlockType:
        if self._is_block_in_chunk(x, y, z):
            return self._block_map[x][y][z]
        return BlockType.Air

    def _is_block_in_chunk(self, x: int, y: int, z: int) -> bool:
        return not (x < 0 or x >= CHUNK_WIDTH or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= CHUNK_WIDTH)