import math
import tkinter as tk
from math import sqrt, acos
from tkinter import ttk
from tkinter import filedialog

from data.Shapes3d import Window3D
from data.Transform3d import Transform3d
from views.NewShapePopup3D import NewShapePopup3D

# Parcialmente gerado por LLM (chat-GPT, modelo especifico desconhecido, very open, openAI)
# prompt utilizado: "Using the TKinter library and the following code as base, generate an interface for transformation of 3D objects, considering that the window will also be a 3D object and thet it does not need special controls anymore, be brief."
#                   seguido do codigo de SideMenu.py

# Apenas os controles de transformacao foram gerados, opcoes de selecao de algoritmo de clipping e utilizacao de arquivos obj foram importadas de SideMenu.py

class SideMenu3D(tk.Frame):
    def __init__(self, parent, viewport, **kwargs):
        super().__init__(parent, **kwargs)
        self.viewport = viewport

        # há um canvas aqui para habilitar scroll no menu lateral
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Eventos da roda do mouse para rolar sem precisar clicar na barra
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/Mac
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux (Scroll Up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux (Scroll Down)

        menu = tk.Frame(self.scrollable_frame, padx=10, pady=10)
        menu.pack(fill="both", expand=True)

        # Object selection
        objects = tk.LabelFrame(menu, text="Objects", padx=5, pady=5)
        objects.pack(fill="x", pady=5)

        self.listbox = tk.Listbox(objects, height=5, exportselection=False)
        self.listbox.pack(fill="x")

        tk.Button(
            objects, text="Add Object",
            command=self.open_create_new_shape
        ).pack(fill="x", pady=5)

        # Translation
        self.translation, self.transFrame = self._create_xyz_section(
            menu, "Translation", ("0", "0", "0")
        )

        # Scaling
        self.scaling, self.scalFrame = self._create_xyz_section(
            menu, "Scaling", ("1", "1", "1"), double=True
        )

        # Seleção do Pivô de Escalonamento
        self.var_tipo_scal = tk.StringVar(value="centro")
        tk.Radiobutton(self.scalFrame, text="Centro do Objeto", variable=self.var_tipo_scal, value="centro").grid(row=1, column=0, columnspan=6)
        tk.Radiobutton(self.scalFrame, text="Origem do Mundo (0,0)", variable=self.var_tipo_scal, value="origem").grid(row=2, column=0, columnspan=6)
        tk.Radiobutton(self.scalFrame, text="Ponto Arbitrário", variable=self.var_tipo_scal, value="arbitrario").grid(row=3, column=0, columnspan=6)

        # Rotation
        self.rotation, self.rotFrame = self._create_xyz_section(
            menu, "Rotation (degrees)", ("0", "0", "0"), double=True, triple=True
        )

        # Seleção do Pivô de Rotação
        self.var_tipo_rot = tk.StringVar(value="centro")
        tk.Radiobutton(self.rotFrame, text="Centro do Objeto", variable=self.var_tipo_rot, value="centro").grid(row=1, column=0, columnspan=6)
        tk.Radiobutton(self.rotFrame, text="Origem do Mundo (0,0)", variable=self.var_tipo_rot, value="origem").grid(row=2, column=0, columnspan=6)
        tk.Radiobutton(self.rotFrame, text="Ponto Arbitrário", variable=self.var_tipo_rot, value="arbitrario").grid(row=3, column=0, columnspan=6)
        tk.Radiobutton(self.rotFrame, text="Eixo Arbitrário", variable=self.var_tipo_rot, value="arbitrario_eixo").grid(row=4, column=0, columnspan=6)
        self.arbitrary_angle = (tk.Entry(self.rotFrame, width=6))
        self.arbitrary_angle.grid(row=7, column=0, columnspan=6)
        self.arbitrary_angle.insert(0, 0)

        tk.Button(
            menu, text="Apply Transformations",
            command=self.apply_transformations
        ).pack(fill="x", pady=10)

        # --- Selecao de algoritmo de clipping ---
        clip_frame = tk.LabelFrame(menu, text="Algoritmo de Clipping de Linha", padx=5, pady=5)
        clip_frame.pack(fill="x", pady=2)

        self.var_tipo_clip = tk.StringVar(value="liang-barsky")
        tk.Radiobutton(clip_frame, text="Liang-Barsky", variable=self.var_tipo_clip, value="liang-barsky",
                       command=self.set_clipping_algorithm).pack(anchor="w")
        tk.Radiobutton(clip_frame, text="Cohen-Sutherland", variable=self.var_tipo_clip, value="cohen-sutherland",
                       command=self.set_clipping_algorithm).pack(anchor="w")


        # --- Selecao de algoritmo de clipping ---
        projection_frame = tk.LabelFrame(menu, text="Tipo de projeção", padx=5, pady=5)
        projection_frame.pack(fill="x", pady=2)

        self.var_tipo_projection = tk.StringVar(value="perspective")
        tk.Radiobutton(projection_frame, text="Ortogonal", variable=self.var_tipo_projection, value="orthogonal", command=self.set_projection_type).grid(row=0, column=0, sticky="W", padx=5)
        tk.Radiobutton(projection_frame, text="Perspectiva", variable=self.var_tipo_projection, value="perspective", command=self.set_projection_type).grid(row=1, column=0, sticky="W", padx=5)
        tk.Label(projection_frame, text="Distância do centro de projeção: ").grid(row=2, column=0, padx=5)
        self.projection_center_distance_entry = tk.Entry(projection_frame, width=6)
        self.projection_center_distance_entry.grid(row=2, column=1, padx=5)
        self.projection_center_distance_entry.insert(0, "1")
        self.projection_center_distance_button = tk.Button(projection_frame, text="Aplicar distância", command=self.set_projection_center_distance)
        self.projection_center_distance_button.grid(row=3, column=0, padx=5)

        file_frame = tk.LabelFrame(menu, text="Arquivos", padx=5, pady=5)
        file_frame.pack(fill="x", pady=10)

        tk.Button(file_frame, text="Salvar", command=self.save_file).pack(fill="x", pady=1)
        tk.Button(file_frame, text="Carregar", command=self.load_file).pack(fill="x", pady=1)

        self.update_list_box()

    def _create_xyz_section(self, parent, title, defaults, double = False, triple = False):
        frame = tk.LabelFrame(parent, text=title, padx=5, pady=5)
        frame.pack(fill="x", pady=5)

        entries = {}

        for i, axis in enumerate(("X", "Y", "Z")):
            tk.Label(frame, text=f"{axis}:").grid(
                row=0, column=i * 2, padx=2
            )

            entry = tk.Entry(frame, width=6)
            entry.insert(0, defaults[i])
            entry.grid(row=0, column=i * 2 + 1, padx=2)

            entries[axis] = entry

        if(double):
            for i, axis in enumerate(("X2", "Y2", "Z2")):
                tk.Label(frame, text=f"{axis}:").grid(
                    row=5, column=i * 2, padx=2
                )

                entry = tk.Entry(frame, width=6)
                entry.insert(0, "0")
                entry.grid(row=5, column=i * 2 + 1, padx=2)

                entries[axis] = entry

        if(triple):
            for i, axis in enumerate(("X3", "Y3", "Z3")):
                tk.Label(frame, text=f"{axis}:").grid(
                    row=6, column=i * 2, padx=2
                )

                entry = tk.Entry(frame, width=6)
                entry.insert(0, "0")
                entry.grid(row=6, column=i * 2 + 1, padx=2)

                entries[axis] = entry

        return entries, frame

    def update_list_box(self):
        self.listbox.delete(0, tk.END)

        for i, shape in enumerate(self.viewport.shapes):
            self.listbox.insert(
                tk.END, getattr(shape, "name", f"Object {i}")
            )

        if self.viewport.shapes:
            self.listbox.selection_set(tk.END)

    def _get_selected_shape(self):
        selection = self.listbox.curselection()

        if not selection:
            return None

        return self.viewport.shapes[selection[0]]

    def open_create_new_shape(self):
        NewShapePopup3D(
            self.winfo_toplevel(),
            self.viewport,
            self.update_list_box
        )

    def apply_transformations(self):
        shape = self._get_selected_shape()

        if shape is None:
            return

        try:
            scalingOffset = None
            if (self.var_tipo_scal.get() != "origem"):
                if(self.var_tipo_scal.get() != "centro"):
                    scalingOffset = [
                        float(self.scaling[a].get())
                        for a in ("X2", "Y2", "Z2")
                    ]
                else: scalingOffset = shape.center()

            rotationOffset = None
            angle_0 = None
            angle_1 = None

            if (self.var_tipo_rot.get() != "origem"):
                if self.var_tipo_rot.get() == "arbitrario":
                    rotationOffset = [
                        float(self.rotation[a].get())
                        for a in ("X2", "Y2", "Z2")
                    ]
                elif self.var_tipo_rot.get() == "arbitrario_eixo":
                    point0 = [
                        float(self.rotation[a].get())
                        for a in ("X2", "Y2", "Z2")
                    ]
                    point1 = [
                        float(self.rotation[a].get())
                        for a in ("X3", "Y3", "Z3")
                    ]
                    rotationOffset = point0

                    x0, y0, z0 = point0
                    x1, y1, z1 = point1

                    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0

                    angle_0 = math.degrees(math.atan2(dz, dx))
                    angle_1 = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
                else:
                    rotationOffset = shape.center()

            translation = [
                float(self.translation[a].get())
                for a in ("X", "Y", "Z")
            ]

            scaling = [
                float(self.scaling[a].get())
                for a in ("X", "Y", "Z")
            ]

            rotation = [
                float(self.rotation[a].get())
                for a in ("X", "Y", "Z")
            ]

            if isinstance(shape, Window3D):
                shape.rotationX += rotation[0]
                shape.rotationY += rotation[1]
                shape.rotationZ += rotation[2]


            # Requires a 3D transformation class and API.
            transform = Transform3d()

            transform.translation(*translation)

            if(scalingOffset is not None):
                transform.translation(-scalingOffset[0], -scalingOffset[1], -scalingOffset[2])
            transform.scale(*scaling)
            if(scalingOffset is not None):
                transform.translation(scalingOffset[0], scalingOffset[1], scalingOffset[2])

            if(rotationOffset is not None):
                transform.translation(-rotationOffset[0], -rotationOffset[1], -rotationOffset[2])
            if(angle_0 is not None and angle_1 is not None):
                transform.rotationX(-angle_0)
                transform.rotationZ(-angle_1)

            if(angle_0 is None and angle_1 is None):
                transform.rotationX(rotation[0])
                transform.rotationY(rotation[1])
                transform.rotationZ(rotation[2])
            else:
                transform.rotationY(float(self.arbitrary_angle.get()))

            if(angle_0 is not None and angle_1 is not None):
                transform.rotationZ(angle_1)
                transform.rotationX(angle_0)
            if(rotationOffset is not None):
                transform.translation(rotationOffset[0], rotationOffset[1], rotationOffset[2])

            transform.apply(shape)
            self.viewport.render()

        except ValueError:
            tk.messagebox.showerror(
                "Invalid input",
                "Enter valid numeric values."
            )

    def set_clipping_algorithm(self):
        algorithm = self.var_tipo_clip.get()
        if(algorithm == "liang-barsky"):
            self.viewport.clippingTool.set_clipping_algorithm_directional(self.viewport.clippingTool.clipLineLiangBarskyDirectional)
            self.viewport.clippingTool.set_clipping_algorithm(self.viewport.clippingTool.clipLineLiangBarsky)
        elif(algorithm == "cohen-sutherland"):
            self.viewport.clippingTool.set_clipping_algorithm_directional(self.viewport.clippingTool.clipLineCohenSutherlandDirectional)
            self.viewport.clippingTool.set_clipping_algorithm(self.viewport.clippingTool.clipLineCohenSutherland)
        self.viewport.render()

    def set_projection_type(self):
        perspective = self.var_tipo_projection.get() == "perspective"
        estado_proj = "normal" if perspective else "disabled"
        self.projection_center_distance_entry.config(state=estado_proj)
        self.projection_center_distance_button.config(state=estado_proj)

        for shape in self.viewport.shapes:
            shape.setDrawmode(perspective)

        self.viewport.render()

    def set_projection_center_distance(self):
        distance = self.projection_center_distance_entry.get()
        self.viewport.perspective_window_distance = float(distance)
        self.viewport.render()

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Salvar Mundo",
            defaultextension=".obj",
            filetypes=[("Arquivos OBJ", "*.obj"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            self.viewport.export_obj3D(filepath)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Carregar Mundo",
            filetypes=[("Arquivos OBJ", "*.obj"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            self.viewport.import_obj3D(filepath)
            self.update_list_box()

    def _on_mousewheel(self, event):
        """Permite rolar o menu usando a rodinha do mouse."""
        # Linux usa Button-4 (Cima) e Button-5 (Baixo)
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")