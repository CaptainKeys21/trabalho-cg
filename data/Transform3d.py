import numpy as np

from data.Shapes2d import Shape2D
from data.WindowData import WindowData

class Transform3d:
    """Sistemas de coordenadas homogêneas (slide 28 - 1.1)
        Está sendo usado o padrão builder nessa classe.
    """

    def __init__(self):
        self.matrix = np.identity(3)

    @staticmethod
    def window_to_ndc(wData: WindowData) -> np.ndarray:
        pass

    def translation(self, dx: float, dy: float, dz: float) -> 'Transform3d':
        res = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [dx,   dy,  dz, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def scale(self, sx: float, sy: float, sz: float) -> 'Transform3d':
        res = np.array([
            [sx,  0.0, 0.0, 0.0],
            [0.0, sy,  0.0, 0.0],
            [0.0, 0.0, sz,  0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def rotationX(self, angle_degree: float) -> 'Transform3d':
        rad = np.radians(angle_degree)
        c, s = np.cos(rad), np.sin(rad)
        res = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0,   c,   s, 0.0],
            [0.0,  -s,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def rotationY(self, angle_degree: float) -> 'Transform3d':
        rad = np.radians(angle_degree)
        c, s = np.cos(rad), np.sin(rad)
        res = np.array([
            [  c, 0.0,  -s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [  s, 0.0,   c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def rotationZ(self, angle_degree: float) -> 'Transform3d':
        rad = np.radians(angle_degree)
        c, s = np.cos(rad), np.sin(rad)
        res = np.array([
            [c,   -s,  0.0, 0.0],
            [s,    c,  0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def apply(self,shape):
        shape.transform(self.matrix)