import math

class Noise:
    def perlin(x: float, y: float) -> float:
        x0: int = int(math.floor(x))
        x1: int = x0 + 1
        y0: int = int(math.floor(y))
        y1: int = y0 + 1
        sx: float = x - float(x0)
        sy: float = y - float(y0)
    
        n0: float = Noise._dot_grid_gradient(x0, y0, x, y)
        n1: float = Noise._dot_grid_gradient(x1, y0, x, y)
        ix0: float = Noise._interpolate(n0, n1, sx)
    
        n0 = Noise._dot_grid_gradient(x0, y1, x, y)
        n1 = Noise._dot_grid_gradient(x1, y1, x, y)
        ix1: float = Noise._interpolate(n0, n1, sx)
    
        value: float = Noise._interpolate(ix0, ix1, sy)
        return value
    
    def _interpolate(a0: float, a1: float, w: float) -> float:
        if 0.0 > w:
            return a0
        if 1.0 < w:
            return a1
        return (a1 - a0) * ((w * (w * 6.0 - 15.0) + 10.0) * w * w * w) + a0

    def _random_gradient(ix: int, iy: int) -> tuple:
        w: int = int(32)
        s: int = int(w / 2)
        a: int = ix
        b: int = iy
        a *= 3284157443
        b ^= a << s | a >> w - s
        b *= 1911520717
        a ^= b << s | b >> w - s
        a *= 2048419325
        random: float = a * (3.14159265 / 2147483648.0)
        v: tuple = (math.cos(random), math.sin(random))
        return v

    def _dot_grid_gradient(ix: int, iy: int, x: float, y: float) -> float:
        gradient: tuple = Noise._random_gradient(ix, iy)
        dx: float = x - float(ix)
        dy: float = y - float(iy)
        return (dx * gradient[0] + dy * gradient[1])