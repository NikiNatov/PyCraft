from Atom import * 

# Noise algorithm from Hopson97's terrain generation
# https://github.com/Hopson97/open-builder/blob/master/src/server/world/terrain_generation.cpp

class Noise:
    Seed: int
    Octaves: int
    Amplitude: float
    Smoothness: float
    Roughness: float
    Offset: float

    def __init__(self, seed: int, octaves: int, amplitude: float, smoothness: float, roughness: float, offset: float):
        self.Seed = seed
        self.Octaves = octaves
        self.Amplitude = amplitude
        self.Smoothness = smoothness
        self.Roughness = roughness
        self.Offset = offset

    def get_noise(self, worldX: float, worldY: float) -> float:
        value: float = 0
        accumulatedAmplitudes: float = 0

        for i in range(self.Octaves):
            frequency: float = Math.pow(2.0, i)
            amplitude: float = Math.pow(self.Roughness, i)
            x: float = worldX * frequency / self.Smoothness
            y: float = worldY * frequency / self.Smoothness
            noise: float = Math.simplex_noise(Vec3(self.Seed + x, self.Seed + y, self.Seed))
            noise = (noise + 1.0) / 2.0
            value += noise * amplitude
            accumulatedAmplitudes += amplitude
        
        return value / accumulatedAmplitudes