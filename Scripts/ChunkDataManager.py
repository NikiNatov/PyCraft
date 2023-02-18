from TerrainGenerator import TerrainGenerator, MeshData
import multiprocessing

class ChunkData:
    block_map: list
    mesh: MeshData

    def __init__(self) -> None:
        self.block_map = []
        self.mesh = MeshData()

class ChunkDataManager:
    _data_gen_processes: list = []
    _process_input_queue: multiprocessing.Queue = multiprocessing.Queue()
    _process_output_queue: multiprocessing.Queue = multiprocessing.Queue()

    def initialize(process_count: int = int(multiprocessing.cpu_count() / 2)) -> None:
        for _ in range(process_count):
            process: multiprocessing.Process = multiprocessing.Process(target = ChunkDataManager._chunk_data_generation_loop, args=(ChunkDataManager._process_input_queue, ChunkDataManager._process_output_queue))
            process.start()
            ChunkDataManager._data_gen_processes.append(process)

    def shutdown() -> None:
        # Insert None inputs so that the the processes exit their while True loop
        for _ in range(len(ChunkDataManager._data_gen_processes)):
            ChunkDataManager._process_input_queue.put(None)

        for process in ChunkDataManager._data_gen_processes:
            process.join()

        ChunkDataManager._data_gen_processes.clear()

    def enqueue_for_update(chunk_coords: tuple, chunk_block_map: list) -> None:
        ChunkDataManager._process_input_queue.put((chunk_coords, chunk_block_map))

    def get_ready_chunk_data(block: bool = False) -> tuple:
        try:
            value = ChunkDataManager._process_output_queue.get(block)
            return value
        except:
            return None

    def _chunk_data_generation_loop(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue) -> None:
        while True:
            result: tuple = input_queue.get()
            if result is None:
                break
            chunk_coords: tuple = result[0]
            chunk_block_map: list = result[1]
            chunk_data: ChunkData = ChunkData()
            chunk_data.block_map = TerrainGenerator.generate_block_map(chunk_coords) if chunk_block_map is None else chunk_block_map
            chunk_data.mesh = TerrainGenerator.generate_mesh_data(chunk_data.block_map)
            output_queue.put((chunk_coords, chunk_data))