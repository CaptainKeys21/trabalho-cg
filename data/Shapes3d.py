from __future__ import annotations

import sys
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

    def __str__(self) -> str:
        return str((self.getX(), self.getY(), self.getZ()))

    def __repr__(self) -> str:
        return self.__str__()

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

    @abstractmethod
    def drawOrtogonal(self, viewport: Viewport):
        pass

    @abstractmethod
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

    def setDrawmode(self, perspective: bool):
        self.drawmode_perspective = perspective

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

    def drawPerspective(self, viewport: Viewport):
        pass

    def drawOrtogonal(self, viewport: Viewport):
        pass

class Polygon3D(Shape3D):
    def __init__(self, name: str, cords: list[Point3D], edges: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)
        self.edges = edges

    def drawOrtogonal(self, viewport: Viewport):
        for point0_f, point1_f in self.edges:
            point0 = int(point0_f)
            point1 = int(point1_f)

            x_vp0, y_vp0 = self.cord_matrix_ndc[point0][:2]
            x_vp1, y_vp1 = self.cord_matrix_ndc[point1][:2]

            if not(self.cord_matrix_ndc[point0][2] < 0 and self.cord_matrix_ndc[point1][2] < 0):

                clipped0, clipped1 = viewport.clippingTool.clippingAlgorithm((x_vp0, y_vp0), (x_vp1, y_vp1))

                if not (clipped0[0] == 0 and clipped0[1] == 0 and clipped1[0] == 0 and clipped1[1] == 0):

                    clipped0x, clipped0y = viewport._ndc_to_viewport(clipped0[0], clipped0[1])
                    clipped1x, clipped1y = viewport._ndc_to_viewport(clipped1[0], clipped1[1])

                    viewport.create_line(clipped0x, clipped0y, clipped1x, clipped1y)

    def drawPerspective(self, viewport: Viewport):
        for point0_f, point1_f in self.edges:
            point0 = int(point0_f)
            point1 = int(point1_f)
            z_vp0 = max(float(self.cord_matrix_ndc_perspective[point0][2]), 1e-9)
            z_vp1 = max(float(self.cord_matrix_ndc_perspective[point1][2]), 1e-9)

            x_vp0 = self.cord_matrix_ndc_perspective[point0][0] * viewport.perspective_window_distance/z_vp0
            y_vp0 = self.cord_matrix_ndc_perspective[point0][1] * viewport.perspective_window_distance/z_vp0
            x_vp1 = self.cord_matrix_ndc_perspective[point1][0] * viewport.perspective_window_distance/z_vp1
            y_vp1 = self.cord_matrix_ndc_perspective[point1][1] * viewport.perspective_window_distance/z_vp1

            if not(self.cord_matrix_ndc_perspective[point0][2] <= 0 and self.cord_matrix_ndc_perspective[point1][2] <= 0):
                clipped0, clipped1 = viewport.clippingTool.clippingAlgorithm((x_vp0, y_vp0), (x_vp1, y_vp1))

                if not (clipped0[0] == 0 and clipped0[1] == 0 and clipped1[0] == 0 and clipped1[1] == 0):
                    clipped0x, clipped0y = viewport._ndc_to_viewport(clipped0[0], clipped0[1])
                    clipped1x, clipped1y = viewport._ndc_to_viewport(clipped1[0], clipped1[1])

                    viewport.create_line(clipped0x, clipped0y, clipped1x, clipped1y, fill=self.color)


class Curve3D(Shape3D):
    def __init__(self, name: str, controlMatrices, method, delta = 0.02, matrixSize = 4, color: str = "#000000"):

        self.delta = delta
        self.method = method
        self.controlMatrices = controlMatrices
        self.matrix_sizes = matrixSize
        self.matrix_amount = len(controlMatrices)

        self.control_matrices = []
        self.control_matrices_perspective = []


        vetor_delta = np.arange(0, 1 + delta, delta)
        self.S = []

        for delta in vetor_delta:
            s = np.array([delta ** 3, delta ** 2, delta, 1])
            self.S.append(s)

        self.T = []
        for s in self.S:
            t = np.array([s]).T
            self.T.append(t)


        method_T = self.method.T
        self.all_points_matrix = []
        for matrix_count in range(0, self.matrix_amount):
            X = []
            Y = []
            Z = []

            for line in controlMatrices[matrix_count]:
                X_line = []
                Y_line = []
                Z_line = []
                for coord in line:
                    X_line.append(coord.getX())
                    Y_line.append(coord.getY())
                    Z_line.append(coord.getZ())
                X.append(X_line)
                Y.append(Y_line)
                Z.append(Z_line)

            px = []
            py = []
            pz = []
            for s in self.S:
                for t in self.T:
                    px.append((s @ self.method @ X @ method_T @ t)[0])
                    py.append((s @ self.method @ Y @ method_T @ t)[0])
                    pz.append((s @ self.method @ Z @ method_T @ t)[0])

            px = np.array(px).reshape((len(self.S), len(self.T)))
            py = np.array(py).reshape((len(self.S), len(self.T)))
            pz = np.array(pz).reshape((len(self.S), len(self.T)))

            for line in range(0, len(px)):
                line_values = []
                for column in range(0, len(px[0])):
                    line_values.append((px[line][column], py[line][column], pz[line][column]))
                self.all_points_matrix.append(line_values)

        arr = []
        for line in self.all_points_matrix:
            for p in line:
                arr.append(Point3D((p[0], p[1], p[2])))
        self.cord_matrix_world = np.array(arr)

        super().__init__(name, arr, color)


    def updateCoordMatrix(self):
        self.all_points_matrix = []
        self.all_points_matrix_perspective = []
        for i in range(0, len(self.S)):
            line = []
            line_perspective = []
            for j in range(0, len(self.T)):
                line.append(self.cord_matrix_ndc[i * len(self.S) + j])
                line_perspective.append(self.cord_matrix_ndc_perspective[i * len(self.S) + j])
            self.all_points_matrix.append(line)
            self.all_points_matrix_perspective.append(line_perspective)


    def drawOrtogonal(self, viewport: Viewport):
        self.updateCoordMatrix()
        for line in range(0, len(self.all_points_matrix)):
            for column in range(0, len(self.all_points_matrix[0])):
                point00 = self.all_points_matrix[line][column]

                if(column + 1 < len(self.all_points_matrix[0])):
                    point01 = self.all_points_matrix[line][column + 1]
                else: point01 = None

                if(line + 1 < len(self.all_points_matrix)):
                    point10 = self.all_points_matrix[line + 1][column]
                else: point10 = None

                if(point01 is not None):
                    clipped0, clipped1 = viewport.clippingTool.clippingAlgorithm((point00[0], point00[1]), (point01[0], point01[1]))
                    if not (clipped0[0] == 0 and clipped0[1] == 0 and clipped1[0] == 0 and clipped1[1] == 0):
                        clipped0x, clipped0y = viewport._ndc_to_viewport(clipped0[0], clipped0[1])
                        clipped1x, clipped1y = viewport._ndc_to_viewport(clipped1[0], clipped1[1])

                        viewport.create_line(clipped0x, clipped0y, clipped1x, clipped1y, fill=self.color)

                if(point10 is not None):
                    clipped2, clipped3 = viewport.clippingTool.clippingAlgorithm((point00[0], point00[1]), (point10[0], point10[1]))
                    if not (clipped2[0] == 0 and clipped2[1] == 0 and clipped3[0] == 0 and clipped3[1] == 0):
                        clipped2x, clipped2y = viewport._ndc_to_viewport(clipped2[0], clipped2[1])
                        clipped3x, clipped3y = viewport._ndc_to_viewport(clipped3[0], clipped3[1])

                        viewport.create_line(clipped2x, clipped2y, clipped3x, clipped3y, fill=self.color)

    def drawPerspective(self, viewport: Viewport):
        self.updateCoordMatrix()
        for line in range(0, len(self.all_points_matrix_perspective)):
            for column in range(0, len(self.all_points_matrix_perspective[0])):
                point00 = self.all_points_matrix_perspective[line][column]

                if(column + 1 < len(self.all_points_matrix_perspective[0])):
                    point01 = self.all_points_matrix_perspective[line][column + 1]
                else: point01 = None

                if(line + 1 < len(self.all_points_matrix_perspective)):
                    point10 = self.all_points_matrix_perspective[line + 1][column]
                else: point10 = None

                z_vp00 = max(float(point00[2]), 1e-9)

                x_vp00 = point00[0] * viewport.perspective_window_distance / z_vp00
                y_vp00 = point00[1] * viewport.perspective_window_distance / z_vp00

                if(point01 is not None and not(point00[2] <= 0 and point01[2] <= 0)):
                    z_vp01 = max(float(point01[2]), 1e-9)
                    x_vp01 = point01[0] * viewport.perspective_window_distance / z_vp01
                    y_vp01 = point01[1] * viewport.perspective_window_distance / z_vp01

                    clipped0, clipped1 = viewport.clippingTool.clippingAlgorithm((x_vp00, y_vp00), (x_vp01, y_vp01))
                    if not (clipped0[0] == 0 and clipped0[1] == 0 and clipped1[0] == 0 and clipped1[1] == 0):
                        clipped0x, clipped0y = viewport._ndc_to_viewport(clipped0[0], clipped0[1])
                        clipped1x, clipped1y = viewport._ndc_to_viewport(clipped1[0], clipped1[1])

                        viewport.create_line(clipped0x, clipped0y, clipped1x, clipped1y, fill=self.color)

                if(point10 is not None and not(point00[2] <= 0 and point10[2] <= 0)):
                    z_vp10 = max(float(point10[2]), 1e-9)
                    x_vp10 = point10[0] * viewport.perspective_window_distance / z_vp10
                    y_vp10 = point10[1] * viewport.perspective_window_distance / z_vp10

                    clipped2, clipped3 = viewport.clippingTool.clippingAlgorithm((x_vp00, y_vp00), (x_vp10, y_vp10))
                    if not (clipped2[0] == 0 and clipped2[1] == 0 and clipped3[0] == 0 and clipped3[1] == 0):
                        clipped2x, clipped2y = viewport._ndc_to_viewport(clipped2[0], clipped2[1])
                        clipped3x, clipped3y = viewport._ndc_to_viewport(clipped3[0], clipped3[1])

                        viewport.create_line(clipped2x, clipped2y, clipped3x, clipped3y, fill=self.color)