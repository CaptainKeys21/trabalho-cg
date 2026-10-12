from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.Viewport import Viewport

from abc import ABC, abstractmethod
import numpy as np

class Shape3D(ABC):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        self.name = name
        self.color = color

        # Coordenadas de mundo
        self.cord_matrix_world = np.array([[x, y, z, 1.0] for x, y, z in cords])

        # Coordenadas Normalizadas, sera preenchido depois
        self.cord_matrix_ndc = np.zeros_like(self.cord_matrix_world)

    @abstractmethod
    def draw(self, viewport: Viewport):
        pass

    def transform(self, matrix: np.ndarray):
        self.cord_matrix_world = self.cord_matrix_world @ matrix

    def center(self) -> tuple[float, float, float]:
        "Equivalente a média aritimética das coordenadas (slide 46 - 1.2)"
        cx, cy, cz = np.mean(self.cord_matrix_world[:, :4], axis=0)
        return float(cx), float(cy), float(cz)

class Point3d(Shape3D):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)


class Window3D(Shape3D):
    def __init__(self, name: str, topRight, topLeft, bottomLeft, bottomRight, color: str = "#000000"):
        super().__init__(name, [topRight, topLeft, bottomLeft, bottomRight], color)
        self.topRight = topRight
        self.topLeft = topLeft
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.rotationX = 0
        self.rotationY = 0
        self.rotationZ = 0

    def height(self):
        return abs(self.topRight[1] - self.bottomRight[1])

    def width(self):
        return abs(self.topRight[0] - self.topLeft[0])
