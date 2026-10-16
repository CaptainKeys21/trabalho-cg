from __future__ import annotations

from math import sqrt
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from views.Viewport import Viewport

from abc import ABC, abstractmethod
import numpy as np


class Point3D():
    def __init__(self, tupl: Tuple[float, float, float]):
        self.x = tupl[0]
        self.y = tupl[1]
        self.z = tupl[2]

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getZ(self):
        return self.z

    def asTuple(self):
        return (self.x, self.y, self.z)

    def asList(self):
        return [self.x, self.y, self.z]

class Shape3D(ABC):
    def __init__(self, name: str, cords: list[Point3D], color: str = "#000000"):
        self.name = name
        self.color = color

        # Coordenadas de mundo
        arr = []
        for p in cords:
            arr.append([p.getX(), p.getY(), p.getZ(), 1.0])
        self.cord_matrix_world = np.array(arr)

        # Coordenadas Normalizadas, sera preenchido depois
        self.cord_matrix_ndc = np.zeros_like(self.cord_matrix_world)
        self.cord_matrix_ndc_perspective = np.zeros_like(self.cord_matrix_world)

        self.drawmode_perspective = True

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

class Point3DRender(Shape3D):
    def __init__(self, name: str, cords: list[Point3D], color: str = "#000000"):
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

    def drawPerspective(self, viewport: Viewport):
        x_vp0 = self.cord_matrix_ndc[0][0]/(self.cord_matrix_ndc[0][2]/viewport.perspective_window_distance)
        y_vp0 = self.cord_matrix_ndc[0][1]/(self.cord_matrix_ndc[0][2]/viewport.perspective_window_distance)
        x_vp, y_vp = viewport._ndc_to_viewport(x_vp0, y_vp0)
        viewport.create_oval(
            x_vp - self.radius,
            y_vp - self.radius,
            x_vp + self.radius,
            y_vp + self.radius,
            fill=self.color
        )

class Window3D(Shape3D):
    def __init__(self, name: str, topRight: Point3D, topLeft: Point3D, bottomLeft: Point3D, bottomRight: Point3D, color: str = "#000000"):
        super().__init__(name, [topRight, topLeft, bottomLeft, bottomRight], color)
        self.topRight = topRight
        self.topLeft = topLeft
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.rotationX = 0
        self.rotationY = 0
        self.rotationZ = 0

    def height(self):
        return abs(self.topRight.getY() - self.bottomRight.getY())

    def width(self):
        return sqrt((self.topRight.getX() - self.topLeft.getX()) ** 2 + (self.topRight.getZ() - self.topLeft.getZ()) ** 2)

class Polygon3D(Shape3D):
    def __init__(self, name: str, cords: list[Point3D], edges: list[tuple[float, float]], color: str = "#000000"):
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

    def drawPerspective(self, viewport: Viewport):
        # print("render")
        for point0, point1 in self.vertices:
            x_vp0 = self.cord_matrix_ndc_perspective[point0][0]/(self.cord_matrix_ndc_perspective[point0][2]/viewport.perspective_window_distance)
            y_vp0 = self.cord_matrix_ndc_perspective[point0][1]/(self.cord_matrix_ndc_perspective[point0][2]/viewport.perspective_window_distance)
            x_vp1 = self.cord_matrix_ndc_perspective[point1][0]/(self.cord_matrix_ndc_perspective[point1][2]/viewport.perspective_window_distance)
            y_vp1 = self.cord_matrix_ndc_perspective[point1][1]/(self.cord_matrix_ndc_perspective[point1][2]/viewport.perspective_window_distance)

            if not(self.cord_matrix_ndc_perspective[point0][2] < 0 and self.cord_matrix_ndc_perspective[point1][2] < 0):
                # print("=============================================================")
                # print(self.cord_matrix_ndc_perspective[point0], self.cord_matrix_ndc_perspective[point1])
                clipped0, clipped1 = viewport.clippingTool.clippingAlgorithm((x_vp0, y_vp0), (x_vp1, y_vp1))

                if not (clipped0[0] == 0 and clipped0[1] == 0 and clipped1[0] == 0 and clipped1[1] == 0):

                    clipped0x, clipped0y = viewport._ndc_to_viewport(clipped0[0], clipped0[1])
                    clipped1x, clipped1y = viewport._ndc_to_viewport(clipped1[0], clipped1[1])
                    # print((clipped0x, clipped0y), (clipped1x, clipped1y))

                    viewport.create_line(clipped0x, clipped0y, clipped1x, clipped1y)