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
        if(abs(self.cord_matrix_ndc[0][0]) > 1 or  # Clipping simples
                abs(self.cord_matrix_ndc[0][1]) > 1): return
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
        ndc0, ndc1 = viewport.clippingTool.clippingAlgorithm(self.cord_matrix_ndc[0], self.cord_matrix_ndc[1])
        x0_vp, y0_vp = viewport._ndc_to_viewport(ndc0[0], ndc0[1])
        x1_vp, y1_vp = viewport._ndc_to_viewport(ndc1[0], ndc1[1])

        viewport.create_line(x0_vp, y0_vp, x1_vp, y1_vp, fill=self.color)

class Polygon(Shape2D):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)

    def draw(self, viewport: Viewport):
        vp_points = []
        ndc_points = []
        for i in range(self.cord_matrix_ndc.shape[0]):
            x_ndc = self.cord_matrix_ndc[i, 0]
            y_ndc = self.cord_matrix_ndc[i, 1]
            ndc_points.append((x_ndc, y_ndc)) # Redireciona as coordenadas normalizadas para receberem clipping

        newLines = viewport.clippingTool.clipPolygonSutherlandHodgeman(ndc_points) # Executa o clipping

        for i in range(0, len(newLines)):
            sx, sy = viewport._ndc_to_viewport(newLines[i][0], newLines[i][1]) # Faz a transformada da viewport
            vp_points.extend([sx, sy]) # Devolve as coordenadas, agora transformadas
        if(len(vp_points) == 0): return # Se todo o poligono esta fora de vista, ignora
        viewport.create_polygon(vp_points, fill=self.color) # Renderiza o poligono