import numpy as np

from data.Shapes2d import Shape2D
from data.WindowData import WindowData

class Transform2d:
    """Sistemas de coordenadas homogêneas (slide 28 - 1.1)
        Está sendo usado o padrão builder nessa classe.
    """

    def __init__(self):
        self.matrix = np.identity(3)

    @staticmethod
    def window_to_ndc(wData: WindowData) -> np.ndarray:
        dx = wData.width()
        dy = wData.height()

        cx = (wData.x_max + wData.x_min) / 2.0
        cy = (wData.y_max + wData.y_min) / 2.0

        t = Transform2d()
        t.translation(-cx, -cy)
        t.rotation(-wData.angle)
        t.escale(2.0 / dx, 2.0 / dy)

        return t.matrix

    def translation(self, dx: float, dy: float) -> 'Transform2d':
        res = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [dx, dy, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def escale(self, sx: float, sy: float) -> 'Transform2d':
        res = np.array([
            [sx,  0.0, 0.0],
            [0.0, sy,  0.0],
            [0.0, 0.0, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def rotation(self, angle_degree: float) -> 'Transform2d':
        rad = np.radians(angle_degree)
        c, s = np.cos(rad), np.sin(rad)
        res = np.array([
            [c,   -s,  0.0],
            [s,    c,  0.0],
            [0.0, 0.0, 1.0]
        ])

        self.matrix = self.matrix @ res
        return self

    def apply(self, shape: Shape2D):
        shape.transform(self.matrix)