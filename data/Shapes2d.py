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

class BezierCurve(Shape2D):
    def __init__(self, name: str, cords: list[tuple[float, float]], color: str = "#000000"):
        super().__init__(name, cords, color)
        self.resolution = 1000

    # A implementação da formula feita nos slides de aula é válida apenas para curvas com 4 pontos aparentemente
    # O Gemini me sugeriu usar curvas de Bernstein, que é válida para N pontos
    # IA usada: Gemini 3.1 Pro (Estendido)
    # Prompt: Vamos adicionar uma Curva Bézier 2D como mais um objeto gráfico na minha interface, no modal de criação de formas deve ter uma opção para curvas bezier e deve ser possível inserir uma quantidade infinita de pontos no formato (x1,y1),(x2,y2),...,(xi,yi)
    def draw(self, viewport: Viewport):
        import math
        pontos_tela = []
        n = self.cord_matrix_ndc.shape[0] - 1  # Grau da curva (N pontos - 1)
        
        # Se não houver pelo menos 2 pontos de controle, não há como desenhar curva
        if n < 1:
            return
            
        # Avalia a curva ao longo do parâmetro 't' de 0.0 a 1.0
        for i in range(self.resolution + 1):
            t = i / self.resolution
            px, py = 0.0, 0.0
            
            # Algoritmo Baseado no Polinômio de Bernstein
            for j in range(n + 1):
                # Coeficiente Binomial (Combinação)
                comb = math.comb(n, j)
                # Termo de Bernstein
                bernstein = comb * ((1 - t) ** (n - j)) * (t ** j)
                
                # Multiplica pelo Ponto de Controle (Lendo do espaço Paralelo/NDC)
                px += bernstein * self.cord_matrix_ndc[j, 0]
                py += bernstein * self.cord_matrix_ndc[j, 1]
            
            # Envia a coordenada Normalizada gerada para os Pixels da Tela
            sx, sy = viewport._ndc_to_viewport(px, py)
            pontos_tela.extend([sx, sy])
            
        # Desenha a curva conectando os pontos de resolução
        if len(pontos_tela) >= 4:
            viewport.create_line(pontos_tela, fill=self.color, width=2)
        