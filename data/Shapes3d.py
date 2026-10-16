from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views.Viewport import Viewport

from abc import ABC, abstractmethod
import numpy as np

class Shape3D(ABC):
    def __init__(self, name: str, cords: list[tuple[float, float, float]], color: str = "#000000"):
        self.name = name
        self.color = color

        # Coordenadas de mundo
        self.cord_matrix_world = np.array([[x, y, z, 1.0] for x, y, z in cords])

        # Coordenadas Normalizadas, sera preenchido depois
        self.cord_matrix_ndc = np.zeros_like(self.cord_matrix_world)

        self.drawmode_perspective = False

    #@abstractmethod # Removido abstract pois nao implementei perspectiva ainda
    def drawOrtogonal(self, viewport: Viewport):
        pass

    #@abstractmethod # Removido abstract pois nao implementei perspectiva ainda
    def drawPerspective(self, viewport: Viewport):
        pass

    def draw(self, viewport: Viewport):
        if self.drawmode_perspective:
            self.drawPerspective(viewport)
        else:
            self.drawOrtogonal(viewport)

    def transform(self, matrix: np.ndarray):
        self.cord_matrix_world = self.cord_matrix_world @ matrix

    def center(self) -> tuple[float, float, float]:
        "Equivalente a média aritimética das coordenadas (slide 46 - 1.2)"
        cx, cy, cz = np.mean(self.cord_matrix_world[:, :3], axis=0)
        return float(cx), float(cy), float(cz)

class Point3d(Shape3D):
    def __init__(self, name: str, cords: list[tuple[float, float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)
        self.radius = 2

    def drawOrtogonal(self, viewport: Viewport):
        x_vp, y_vp = viewport._ndc_to_viewport(*self.cord_matrix_ndc[0][:2])
        viewport.create_oval(
            x_vp - self.radius,
            y_vp - self.radius,
            x_vp + self.radius,
            y_vp + self.radius,
            fill=self.color
        )

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

class Polygon3D(Shape3D):
    def __init__(self, name: str, cords: list[tuple[float, float, float]], edges: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)
        self.vertices = edges

    def drawOrtogonal(self, viewport: Viewport):
        for point0, point1 in self.vertices:
            x_vp0, y_vp0 = self.cord_matrix_ndc[point0][:2]
            x_vp1, y_vp1 = self.cord_matrix_ndc[point1][:2]

            if not(self.cord_matrix_ndc[point0][2] < 0 and self.cord_matrix_ndc[point1][2] < 0):

                clipped0, clipped1 = viewport.clippingTool.clippingAlgorithm((x_vp0, y_vp0), (x_vp1, y_vp1))

                if not (clipped0[0] == 0 and clipped0[1] == 0 and clipped1[0] == 0 and clipped1[1] == 0):

                    clipped0x, clipped0y = viewport._ndc_to_viewport(clipped0[0], clipped0[1])
                    clipped1x, clipped1y = viewport._ndc_to_viewport(clipped1[0], clipped1[1])

                    viewport.create_line(clipped0x, clipped0y, clipped1x, clipped1y)