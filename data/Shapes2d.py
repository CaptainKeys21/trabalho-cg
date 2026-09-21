from __future__ import annotations
from typing import TYPE_CHECKING

from numpy.f2py.crackfortran import previous_context

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
        if(len(vp_points) == 0): return # Se t odo o poligono esta fora de vista, ignora
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

        previous = (-1, -1) # Sinaliza que o primeiro ponto nao foi inicializado
        segments = 1 # Quantidade de segmentos da curva
        previousCutoff = False # Se a ultima reta foi cortada

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

            if(previous[0] != -1 or previous[1] != -1): # Se nao e o primeiro ponto
                clip0, clip1 = viewport.clippingTool.clippingAlgorithm(previous, (px, py)) # Roda o clipping
                if(clip0 != (0, 0) or clip1 != (0, 0)): # Se pelo menos um dos pontos esta dentro da viewport
                    if(previousCutoff): # Se a ultima reta foi cortada
                        previousCutoff = False
                        segments += 1 # Aumenta a quantidade de segmentos

                    if(abs(clip0[0] - previous[0]) >= 0.001 or abs(clip0[1] - previous[1]) > 0.001): # Se o primeiro ponto recebeu clipping, abs e usado por causa de imprecisoes de ponto flutuante fazendo os dois valores serem diferentes por < 10e-17
                        sx0, sy0 = viewport._ndc_to_viewport(clip0[0], clip0[1])# Transforma e
                        pontos_tela.extend([sx0, sy0])                          # adiciona ele

                    sx0, sy0 = viewport._ndc_to_viewport(clip1[0], clip1[1])    # Transforma e
                    pontos_tela.extend([sx0, sy0])                              # adiciona o segundo ponto

                    if(abs(clip1[0] - px) >= 0.001 or abs(clip1[1] - py) >= 0.001): # Se o segundo ponto recebeu clipping
                        pontos_tela.extend([-1]) # Adiciona um marcador
                        previousCutoff = True    # Marca que a ultima reta foi cortada

            elif(abs(px) <= 1 and abs(py) <= 1): # Se e o primeiro ponto e ele esta dentro da viewport
                sx, sy = viewport._ndc_to_viewport(px, py)  # Transforma e
                pontos_tela.extend([sx, sy])                # adiciona ele
                previous = (px, py) # Coloca ele como o primeiro
            
        # Desenha a curva conectando os pontos de resolução
        if len(pontos_tela) >= 4 + segments: # Se ha pontos o suficiente para desenhar uma linha
            pontos_segmentos = self.splitAt(pontos_tela, -1) # Separa os segmentos utilizando o marcador
            for k in range(0, len(pontos_segmentos)):   # Para t odo segmento
                if (len(pontos_segmentos[k]) >= 4):     # Se tem pontos o suficiente
                    viewport.create_line(pontos_segmentos[k], fill=self.color, width=2) # Desenha ele

    def splitAt(self, list, value): # Utilizado para separar as listas de pontos de cada segmento
        lists = []
        lists.append([])
        previous_list = 0
        for i in range(0, len(list)):
            if(list[i] != value):
                lists[previous_list].append(list[i])
            else:
                previous_list += 1
                lists.append([])
        return lists