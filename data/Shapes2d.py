from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.Viewport import Viewport

from abc import ABC, abstractmethod
import numpy as np

class Shape2D(ABC):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        self.name = name
        self.color = color

        # Coordenadas de mundo
        self.cord_matrix_world = np.array([[x, y, 1.0] for x, y in cords])

        # Coordenadas Normalizadas, sera preenchido depois
        self.cord_matrix_ndc = np.zeros_like(self.cord_matrix_world)

    @abstractmethod
    def draw(self, viewport: Viewport):
        pass

    def transform(self, matrix: np.ndarray):
        self.cord_matrix_world = self.cord_matrix_world @ matrix

    def center(self) -> tuple[float, float]:
        "Equivalente a média aritimética das coordenadas (slide 46 - 1.2)"
        cx, cy = np.mean(self.cord_matrix_world[:, :2], axis=0)
        return float(cx), float(cy)

class Point(Shape2D):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)
        self.radius = 2 # só pra dar tamanho ao ponto

    def draw(self, viewport: Viewport):
        x_vp, y_vp = viewport._ndc_to_viewport(*self.cord_matrix_ndc[0][:2])
        viewport.create_oval(
            x_vp - self.radius, 
            y_vp - self.radius, 
            x_vp + self.radius, 
            y_vp + self.radius, 
            fill=self.color
        )

class Line(Shape2D):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)

    def draw(self, viewport: Viewport):
        x0_vp, y0_vp = viewport._ndc_to_viewport(*self.cord_matrix_ndc[0][:2])
        x1_vp, y1_vp = viewport._ndc_to_viewport(*self.cord_matrix_ndc[1][:2])

        viewport.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=self.color)

class Polygon(Shape2D):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)

    def draw(self, viewport: Viewport):
        vp_points = []

        for i in range(self.cord_matrix_ndc.shape[0]):
            x_ndc = self.cord_matrix_ndc[i, 0]
            y_ndc = self.cord_matrix_ndc[i, 1]

            sx, sy = viewport._ndc_to_viewport(x_ndc, y_ndc)
            vp_points.extend([sx, sy])

        viewport.create_polygon(vp_points, fill=self.color)