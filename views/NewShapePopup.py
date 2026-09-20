from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.Viewport import Viewport

import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
import math
from data.Shapes2d import Point, Line, Polygon, BezierCurve

class NewShapePopup(tk.Toplevel):
    def __init__(self, parent, viewport: Viewport, on_add_callback):
        super().__init__(parent)
        self.title("Adicionar Nova Forma")
        self.geometry("300x420") 
        self.transient(parent)
        self.grab_set()
        
        self.viewport = viewport
        self.on_add_callback = on_add_callback
        
        # --- Nome da Forma ---
        tk.Label(self, text="Nome da Forma:").pack(anchor="w", padx=10, pady=(10, 0))
        self.ent_nome = tk.Entry(self)
        self.ent_nome.insert(0, "Novo Objeto")
        self.ent_nome.pack(fill="x", padx=10)

        # --- Cor da Forma ---
        tk.Label(self, text="Cor da Forma:").pack(anchor="w", padx=10, pady=(10, 0))
        
        self.selected_color = "#3498db" 
        
        frame_cor = tk.Frame(self)
        frame_cor.pack(fill="x", padx=10)
        
        # Botão que mostra a cor atual visualmente
        self.btn_color = tk.Button(frame_cor, bg=self.selected_color, width=4, command=self._open_colorpicker)
        self.btn_color.pack(side="left")
        
        tk.Button(frame_cor, text="Alterar Cor", command=self._open_colorpicker).pack(side="left", padx=5)
        
        # --- Tipo de Forma ---
        tk.Label(self, text="Tipo de Forma:").pack(anchor="w", padx=10, pady=(10, 0))
        self.var_tipo = tk.StringVar(value="Ponto")
        opcoes = [
            "Ponto", "Reta", "Polígono (Triângulo)", "Polígono (Quadrado)", 
            "Polígono (Pentágono)", "Polígono (Hexágono)", "Polígono (Customizado)",
            "Curva Bézier"
        ]
        combo = ttk.Combobox(self, textvariable=self.var_tipo, values=opcoes, state="readonly")
        combo.pack(fill="x", padx=10)
        combo.bind("<<ComboboxSelected>>", self._toggle_entradas)
        
        # --- Campo Vértices Customizados ---
        tk.Label(self, text="Custom / Bézier (ex: 0,0; 10,0; 5,10):").pack(anchor="w", padx=10, pady=(10, 0))
        self.ent_custom = tk.Entry(self, state="disabled")
        # Colocando um placeholder condizente
        self.ent_custom.insert(0, "0,0; 20,20; 40,0; 60,20;")
        self.ent_custom.pack(fill="x", padx=10)
        
        # --- Posição Inicial ---
        tk.Label(self, text="Posição Inicial (Offset):").pack(anchor="w", padx=10, pady=(10, 0))
        self.var_pos = tk.StringVar(value="origem")
        tk.Radiobutton(self, text="Origem (0, 0)", variable=self.var_pos, value="origem", command=self._toggle_entradas).pack(anchor="w", padx=10)
        tk.Radiobutton(self, text="Ponto Arbitrário", variable=self.var_pos, value="arbitrario", command=self._toggle_entradas).pack(anchor="w", padx=10)
        
        frame_coords = tk.Frame(self)
        frame_coords.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_coords, text="X:").pack(side="left")
        self.ent_x = tk.Entry(frame_coords, width=7, state="disabled")
        self.ent_x.insert(0, "0")
        self.ent_x.pack(side="left", padx=(2, 10))
        tk.Label(frame_coords, text="Y:").pack(side="left")
        self.ent_y = tk.Entry(frame_coords, width=7, state="disabled")
        self.ent_y.insert(0, "0")
        self.ent_y.pack(side="left", padx=2)
        
        tk.Button(self, text="Adicionar", command=self.criar_forma, bg="#27ae60", fg="white").pack(fill="x", padx=10, pady=15)

    def _toggle_entradas(self, event=None):
        estado_pos = "normal" if self.var_pos.get() == "arbitrario" else "disabled"
        self.ent_x.config(state=estado_pos)
        self.ent_y.config(state=estado_pos)
        
        # Libera o campo customizado tanto para Polígono quanto para Bézier
        tipo = self.var_tipo.get()
        estado_custom = "normal" if tipo in ["Polígono (Customizado)", "Curva Bézier"] else "disabled"
        self.ent_custom.config(state=estado_custom)

    def _gerar_poligono_regular(self, cx: float, cy: float, lados: int, raio: float = 15.0):
        """Gera os vértices distribuídos de forma equidistante ao redor de um centro."""
        pontos = []
        for i in range(lados):
            # Subtrair PI/2 garante que o primeiro vértice sempre aponte para o topo
            angulo = 2 * math.pi * i / lados - math.pi / 2
            px = cx + raio * math.cos(angulo)
            py = cy + raio * math.sin(angulo)
            pontos.append((px, py))
        return pontos

    def _open_colorpicker(self):
        chosen_color = colorchooser.askcolor(color=self.selected_color, title="Escolha a cor da forma")
        
        # Se o usuário não cancelar a janela (chosen_color[1] não for None)
        if chosen_color[1]:
            self.selected_color = chosen_color[1]
            self.btn_color.config(bg=self.selected_color)

    def criar_forma(self):
        try:
            nome = self.parse_name()
            x = 0.0 if self.var_pos.get() == "origem" else float(self.ent_x.get())
            y = 0.0 if self.var_pos.get() == "origem" else float(self.ent_y.get())
            tipo = self.var_tipo.get()
            
            if tipo == "Ponto":
                forma = Point(nome, [(x, y)], color=self.selected_color)
            elif tipo == "Reta":
                forma = Line(nome, [(x, y), (x + 20, y + 20)], color=self.selected_color)
            elif tipo == "Polígono (Triângulo)":
                forma = Polygon(nome, [(x, y), (x + 20, y), (x + 10, y + 20)], color=self.selected_color)
            elif tipo == "Polígono (Quadrado)":
                forma = Polygon(nome, [(x, y), (x + 20, y), (x + 20, y + 20), (x, y + 20)], color=self.selected_color)
            elif tipo == "Polígono (Pentágono)":
                pontos = self._gerar_poligono_regular(x, y, lados=5, raio=20)
                forma = Polygon(nome, pontos, color=self.selected_color)
            elif tipo == "Polígono (Hexágono)":
                pontos = self._gerar_poligono_regular(x, y, lados=6, raio=20)
                forma = Polygon(nome, pontos, color=self.selected_color)
            elif tipo == "Polígono (Customizado)":
                pontos = []
                # Divide a string nos separadores e converte para (X, Y)
                raw_pontos = self.ent_custom.get().split(';')
                for par in raw_pontos:
                    px, py = par.split(',')
                    # Adiciona a posição base digitada aos vértices relativos
                    pontos.append((x + float(px.strip()), y + float(py.strip())))
                forma = Polygon(nome, pontos, color=self.selected_color)
            elif tipo == "Curva Bézier":
                pontos = []
                # Divide a string nos separadores e converte para (X, Y)
                raw_pontos = self.ent_custom.get().split(';')
                for par in raw_pontos:
                    px, py = par.split(',')
                    # Adiciona a posição base digitada aos vértices relativos
                    pontos.append((x + float(px.strip()), y + float(py.strip())))
                forma = BezierCurve(nome, pontos, color=self.selected_color)
            else:
                raise ValueError
                
            self.viewport.add_shape(forma)
            self.on_add_callback()
            self.destroy()
            
        except ValueError:
            # Em caso de erro, só não faz nada
            pass

    def parse_name(self):
        nome = self.ent_nome.get().strip() or "Objeto Sem Nome"

        existing_names = {shape.name for shape in self.viewport.shapes if hasattr(shape, 'name')}

        if nome not in existing_names:
            return nome

        counter = 1
        while True:
            new_name = f"{nome} ({counter})"
            if new_name not in existing_names:
                return new_name
            counter += 1
