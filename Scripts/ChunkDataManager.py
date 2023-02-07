from TerrainGenerator import *
import multiprocessing

class ChunkData:
    BlockMap: list
    Mesh: MeshData

    def __init__(self) -> None:
        self.BlockMap = []
        self.Mesh = MeshData()

class ChunkDataManager:
    _DataGenProcesses: list = []
    _ProcessInputQueue: multiprocessing.Queue = multiprocessing.Queue()
    _ProcessOutputQueue: multiprocessing.Queue = multiprocessing.Queue()

    def initialize() -> None:
        for _ in range(int(multiprocessing.cpu_count() / 2)):
            process: multiprocessing.Process = multiprocessing.Process(target = ChunkDataManager._chunk_data_generation_loop, args=(ChunkDataManager._ProcessInputQueue, ChunkDataManager._ProcessOutputQueue))
            process.start()
            ChunkDataManager._DataGenProcesses.append(process)

    def shutdown() -> None:
        # Insert None inputs so that the the processes exit their while True loop
        for _ in range(len(ChunkDataManager._DataGenProcesses)):
            ChunkDataManager._ProcessInputQueue.put(None)

        for process in ChunkDataManager._DataGenProcesses:
            process.join()

        ChunkDataManager._DataGenProcesses.clear()

    def enqueue_for_update(chunkCoords: tuple, chunkBlockMap: list) -> None:
        ChunkDataManager._ProcessInputQueue.put((chunkCoords, chunkBlockMap))

    def get_ready_chunk_data() -> ChunkData:
        try:
            value = ChunkDataManager._ProcessOutputQueue.get_nowait()
            return value
        except:
            return None

    def _chunk_data_generation_loop(inputQueue: multiprocessing.Queue, outputQueue: multiprocessing.Queue) -> None:
        while True:
            result: tuple = inputQueue.get()
            if result is None:
                break
            chunkCoords: tuple = result[0]
            chunkBlockMap: list = result[1]
            chunkData: ChunkData = ChunkData()
            chunkData.BlockMap = TerrainGenerator.generate_block_map(chunkCoords) if chunkBlockMap is None else chunkBlockMap
            chunkData.Mesh = TerrainGenerator.generate_mesh_data(chunkData.BlockMap)
            outputQueue.put((chunkCoords, chunkData))