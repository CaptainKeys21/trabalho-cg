from tkinter import Canvas

from data.ClippingTool import ClippingTool
from data.ViewportData import ViewportData
from data.WindowData import WindowData
from data.Shapes2d import Shape2D
from data.Transform2d import Transform2d
from data.ObjConverter import ObjConverter
import numpy as np
class Viewport(Canvas):
    def __init__(self, parent):
        self.vpData = ViewportData(x_min=0, y_min=0, x_max=600, y_max=600) # As coordenadas mínimas não podem ser menores que 0
        self.wData = WindowData(x_min=-250, y_min=-250, x_max=250, y_max=250)
        self.clippingTool = ClippingTool(-1, 1, -1, 1)
        np.set_printoptions(legacy='1.25')
        super().__init__(
            parent, 
            bg="white",
            highlightthickness=0,
            width=int(self.vpData.width()) + 25,
            height=int(self.vpData.height()) + 25,
        )

        # Armazenamento de formas (em coordenadas de mundo)
        self.shapes: list[Shape2D] = []

        self._draw_crosshair()
        self._draw_window_border()

    def _ndc_to_viewport(self, x_ndc: float, y_ndc: float) -> tuple[float, float]:
        sx = self.vpData.x_min + ((x_ndc + 1.0) / 2.0) * self.vpData.width()
        sy = self.vpData.y_min + ((1.0 - y_ndc) / 2.0) * self.vpData.height()

        return sx, sy

    def update_ndc_display_file(self):
        matrix_ndc = Transform2d.window_to_ndc(self.wData)

        for shape in self.shapes:
            shape.cord_matrix_ndc = shape.cord_matrix_world @ matrix_ndc

    def _world_to_viewport(self, xw: float, yw: float) -> tuple[float, float]:
        """Transformada de viewport (slide 28 - 1.1)"""
        u = (xw - self.wData.x_min) / self.wData.width()
        v = (yw - self.wData.y_min) / self.wData.height()

        x_vp = u * self.vpData.width()
        y_vp = (1 - v) * self.vpData.height()

        return x_vp, y_vp
    
    def _draw_crosshair(self):
        cx = self.wData.x_min + self.wData.width() / 2.0
        cy = self.wData.y_min + self.wData.height() / 2.0

        sx, sy = self._world_to_viewport(cx, cy)

        # Tamanho da linha da mira em pixels
        t = 10 

        self.create_line(sx - t, sy, sx + t, sy, fill="red", width=1)
        self.create_line(sx, sy - t, sx, sy + t, fill="red", width=1)

    def _draw_window_border(self):
        xw_min, yw_min = self.wData.x_min, self.wData.y_min
        xw_max, yw_max = self.wData.x_max, self.wData.y_max

        sx1, sy1 = self._world_to_viewport(xw_min, yw_min)
        sx2, sy2 = self._world_to_viewport(xw_max, yw_max)

        self.create_rectangle(
            sx1, sy1, sx2, sy2, 
            outline="#3498db", 
            width=2, 
            dash=(4, 4)
        )

    def add_shape(self, shape: Shape2D):
        self.shapes.append(shape)
        self.render()

    def render(self):
        self.delete("all")

        self.update_ndc_display_file()

        for shape in self.shapes:
            shape.draw(self)

        self._draw_crosshair()
        self._draw_window_border()

    def pan(self, dx: float, dy: float):
        self.wData.x_min += dx
        self.wData.x_max += dx
        self.wData.y_min += dy
        self.wData.y_max += dy

        self.render()

    def zoom(self, factor: float):
        current_width = self.wData.width()
        current_height = self.wData.height()

        cx = self.wData.x_min + current_width / 2.0
        cy = self.wData.y_min + current_height / 2.0

        nova_largura = current_width * factor
        nova_altura = current_height * factor

        self.wData.x_min = cx - nova_largura / 2.0
        self.wData.x_max = cx + nova_largura / 2.0
        self.wData.y_min = cy - nova_altura / 2.0
        self.wData.y_max = cy + nova_altura / 2.0

        self.render()

    def rotate(self, angle_degree: float):
        self.wData.angle += angle_degree
        self.render()

    def export_obj(self, filepath: str):
        ObjConverter._export(filepath, self.shapes)

    def import_obj(self, filepath: str):
        self.shapes = ObjConverter._import(filepath)
        self.render()
                 
