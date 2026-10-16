from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.Viewport import Viewport

import tkinter as tk
from tkinter import ttk, colorchooser

from data.Shapes3d import Point3d, Polygon3D

# Parcialmente gerado por LLM (chat-GPT, modelo especifico desconhecido, very open, openAI)
# prompt utilizado: "Based on the following code, generate an alternate version of this custom TKinter class to only support 3D points and polygons. Polygons need an additional field for the description of their edges."
#                   seguido do codigo de NewShapePopup.py

class NewShapePopup3D(tk.Toplevel):
    def __init__(self, parent, viewport: Viewport, on_add_callback):
        super().__init__(parent)

        self.title("Adicionar Nova Forma 3D")
        self.geometry("350x550")
        self.transient(parent)
        self.grab_set()

        self.viewport = viewport
        self.on_add_callback = on_add_callback

        # --- Nome da Forma ---
        tk.Label(self, text="Nome da Forma:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )

        self.ent_nome = tk.Entry(self)
        self.ent_nome.insert(0, "Novo Objeto 3D")
        self.ent_nome.pack(fill="x", padx=10)

        # --- Cor da Forma ---
        tk.Label(self, text="Cor da Forma:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )

        self.selected_color = "#3498db"

        frame_cor = tk.Frame(self)
        frame_cor.pack(fill="x", padx=10)

        self.btn_color = tk.Button(
            frame_cor,
            bg=self.selected_color,
            width=4,
            command=self._open_colorpicker
        )
        self.btn_color.pack(side="left")

        tk.Button(
            frame_cor,
            text="Alterar Cor",
            command=self._open_colorpicker
        ).pack(side="left", padx=5)

        # --- Tipo de Forma ---
        tk.Label(self, text="Tipo de Forma:").pack(
            anchor="w", padx=10, pady=(10, 0)
        )

        self.var_tipo = tk.StringVar(value="Ponto 3D")

        self.combo_tipo = ttk.Combobox(
            self,
            textvariable=self.var_tipo,
            values=["Ponto 3D", "Polígono 3D"],
            state="readonly"
        )
        self.combo_tipo.pack(fill="x", padx=10)
        self.combo_tipo.bind(
            "<<ComboboxSelected>>",
            self._toggle_entradas
        )

        # --- Vértices 3D ---
        tk.Label(
            self,
            text="Vértices 3D (x,y,z; x,y,z; ...):"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.ent_custom = tk.Entry(self)
        self.ent_custom.insert(
            0,
            "-100,-100,100; 100,-100,100; 100,100,100; -100,100,100; -100,-100,300; 100,-100,300; 100,100,300; -100,100,300"
        )
        self.ent_custom.pack(fill="x", padx=10)

        # --- Descrição das Arestas ---
        tk.Label(
            self,
            text="Descrição das Arestas:"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.ent_edge_description = tk.Entry(self)
        self.ent_edge_description.insert(
            0,
            "(0, 1),(1, 2),(2, 3),(3, 0),(0, 4),(1, 5),(2, 6),(3, 7),(4, 5),(5, 6),(6, 7),(7, 4)"
        )
        self.ent_edge_description.pack(fill="x", padx=10)

        # --- Posição Inicial ---
        tk.Label(
            self,
            text="Posição Inicial (Offset):"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.var_pos = tk.StringVar(value="origem")

        tk.Radiobutton(
            self,
            text="Origem (0, 0, 0)",
            variable=self.var_pos,
            value="origem",
            command=self._toggle_entradas
        ).pack(anchor="w", padx=10)

        tk.Radiobutton(
            self,
            text="Ponto Arbitrário",
            variable=self.var_pos,
            value="arbitrario",
            command=self._toggle_entradas
        ).pack(anchor="w", padx=10)

        # --- Coordenadas do Offset ---
        frame_coords = tk.Frame(self)
        frame_coords.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_coords, text="X:").pack(side="left")

        self.ent_x = tk.Entry(frame_coords, width=6, state="disabled")
        self.ent_x.insert(0, "0")
        self.ent_x.pack(side="left", padx=(2, 8))

        tk.Label(frame_coords, text="Y:").pack(side="left")

        self.ent_y = tk.Entry(frame_coords, width=6, state="disabled")
        self.ent_y.insert(0, "0")
        self.ent_y.pack(side="left", padx=(2, 8))

        tk.Label(frame_coords, text="Z:").pack(side="left")

        self.ent_z = tk.Entry(frame_coords, width=6, state="disabled")
        self.ent_z.insert(0, "0")
        self.ent_z.pack(side="left", padx=2)

        # --- Botão Adicionar ---
        tk.Button(
            self,
            text="Adicionar",
            command=self.criar_forma,
            bg="#27ae60",
            fg="white"
        ).pack(fill="x", padx=10, pady=15)

        self._toggle_entradas()

    # ---------------------------------------------------------
    # Interface
    # ---------------------------------------------------------

    def _toggle_entradas(self, event=None):
        """Atualiza os campos conforme o tipo de forma selecionado."""

        estado_pos = (
            "normal"
            if self.var_pos.get() == "arbitrario"
            else "disabled"
        )

        self.ent_x.config(state=estado_pos)
        self.ent_y.config(state=estado_pos)
        self.ent_z.config(state=estado_pos)

        tipo = self.var_tipo.get()

        # Os vértices são editáveis apenas para polígonos.
        estado_vertices = (
            "normal" if tipo == "Polígono 3D" else "disabled"
        )

        self.ent_custom.config(state=estado_vertices)

        # A descrição das arestas só se aplica a polígonos.
        estado_arestas = (
            "normal" if tipo == "Polígono 3D" else "disabled"
        )

        self.ent_edge_description.config(state=estado_arestas)

    def _open_colorpicker(self):
        """Abre o seletor de cores."""

        chosen_color = colorchooser.askcolor(
            color=self.selected_color,
            title="Escolha a cor da forma"
        )

        if chosen_color[1]:
            self.selected_color = chosen_color[1]
            self.btn_color.config(bg=self.selected_color)

    # ---------------------------------------------------------
    # Coordenadas
    # ---------------------------------------------------------

    def _parse_offset(self):
        """Obtém o deslocamento inicial em 3D."""

        if self.var_pos.get() == "origem":
            return 0.0, 0.0, 0.0

        x = float(self.ent_x.get())
        y = float(self.ent_y.get())
        z = float(self.ent_z.get())

        return x, y, z

    def _parse_vertices(self, offset):
        """
        Converte uma string como:
            0,0,0; 20,0,0; 10,20,10

        em uma lista de pontos 3D, aplicando o deslocamento.
        """

        ox, oy, oz = offset
        vertices = []

        raw_vertices = self.ent_custom.get().strip()

        if not raw_vertices:
            raise ValueError("Informe pelo menos um vértice.")

        for item in raw_vertices.split(";"):
            item = item.strip()

            # Permite um ponto e vírgula opcional no final.
            if not item:
                continue

            coords = item.split(",")

            if len(coords) != 3:
                raise ValueError(
                    f"Coordenada inválida: '{item}'. "
                    "Use o formato x,y,z."
                )

            px, py, pz = (
                float(coord.strip())
                for coord in coords
            )

            vertices.append(
                (ox + px, oy + py, oz + pz)
            )

        if not vertices:
            raise ValueError("Nenhum vértice válido foi informado.")

        return vertices

    # ---------------------------------------------------------
    # Criação das formas
    # ---------------------------------------------------------

    def criar_forma(self):
        """Cria e adiciona um ponto 3D ou polígono 3D."""

        try:
            nome = self.parse_name()
            tipo = self.var_tipo.get()
            offset = self._parse_offset()

            if tipo == "Ponto 3D":
                forma = Point3d(
                    nome,
                    [offset],
                    color=self.selected_color
                )

            elif tipo == "Polígono 3D":
                vertices = self._parse_vertices(offset)

                if len(vertices) < 3:
                    raise ValueError(
                        "Um polígono precisa de pelo menos "
                        "3 vértices."
                    )

                edge_points = self.ent_edge_description.get().replace(' ', '').replace('(', '').replace(')', '') .split(',')
                print(edge_points)
                edges = []
                for i in range(0, int(len(edge_points)/2)):
                    edges.append((int(edge_points[i * 2]), int(edge_points[i * 2 + 1])))

                forma = Polygon3D(
                    nome,
                    vertices,
                    edges=edges,
                    color=self.selected_color
                )

            else:
                raise ValueError("Tipo de forma inválido.")

            self.viewport.add_shape3D(forma)
            self.on_add_callback()
            self.destroy()

        except ValueError as error:
            tk.messagebox.showerror(
                "Erro ao criar forma",
                str(error),
                parent=self
            )

    # ---------------------------------------------------------
    # Nome único
    # ---------------------------------------------------------

    def parse_name(self):
        """Garante que o nome da forma seja único."""

        nome = self.ent_nome.get().strip() or "Objeto 3D Sem Nome"

        existing_names = {
            shape.name
            for shape in self.viewport.shapes
            if hasattr(shape, "name")
        }

        if nome not in existing_names:
            return nome

        counter = 1

        while True:
            new_name = f"{nome} ({counter})"

            if new_name not in existing_names:
                return new_name

            counter += 1
