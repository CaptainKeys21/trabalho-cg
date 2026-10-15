import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from data.Shapes3d import Window3D
from data.Transform3d import Transform3d
from views.NewShapePopup import NewShapePopup

# Parcialmente gerado por LLM (chat-GPT, modelo especifico desconhecido, very open, openAI)
# prompt utilizado: "Using the TKinter library and the following code as base, generate an interface for transformation of 3D objects, considering that the window will also be a 3D object and thet it does not need special controls anymore, be brief."
#                   seguido do codigo de SideMenu.py

# Apenas os controles de transformacao foram gerados, opcoes de selecao de algoritmo de clipping e utilizacao de arquivos obj foram importadas de SideMenu.py

class SideMenu3D(tk.Frame):
    def __init__(self, parent, viewport, **kwargs):
        super().__init__(parent, **kwargs)
        self.viewport = viewport

        menu = tk.Frame(self, padx=10, pady=10)
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
            menu, "Scaling", ("1", "1", "1")
        )

        # Seleção do Pivô de Escalonamento
        self.var_tipo_rot = tk.StringVar(value="centro")
        # tk.Radiobutton(self.scalFrame, text="Centro do Objeto", variable=self.var_tipo_rot, value="centro").grid(row=1, column=0)
        # tk.Radiobutton(self.scalFrame, text="Origem do Mundo (0,0)", variable=self.var_tipo_rot, value="origem").grid(row=2, column=0)
        # tk.Radiobutton(self.scalFrame, text="Ponto Arbitrário", variable=self.var_tipo_rot, value="arbitrario").grid(row=3, column=0)

        # Rotation
        self.rotation, self.rotFrame = self._create_xyz_section(
            menu, "Rotation (degrees)", ("0", "0", "0")
        )

        # Seleção do Pivô de Rotação
        self.var_tipo_rot = tk.StringVar(value="centro")
        tk.Radiobutton(self.rotFrame, text="Centro do Objeto", variable=self.var_tipo_rot, value="centro")
        tk.Radiobutton(self.rotFrame, text="Origem do Mundo (0,0)", variable=self.var_tipo_rot, value="origem")
        tk.Radiobutton(self.rotFrame, text="Ponto Arbitrário", variable=self.var_tipo_rot, value="arbitrario")

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

        file_frame = tk.LabelFrame(menu, text="Arquivos", padx=5, pady=5)
        file_frame.pack(fill="x", pady=10)

        tk.Button(file_frame, text="Salvar", command=self.save_file).pack(fill="x", pady=1)
        tk.Button(file_frame, text="Carregar", command=self.load_file).pack(fill="x", pady=1)

        self.update_list_box()

    def _create_xyz_section(self, parent, title, defaults):
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
        NewShapePopup(
            self.winfo_toplevel(),
            self.viewport,
            self.update_list_box
        )

    def apply_transformations(self):
        shape = self._get_selected_shape()

        if shape is None:
            return

        try:
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
            transform.scale(*scaling)
            transform.rotationX(rotation[0])
            transform.rotationY(rotation[1])
            transform.rotationZ(rotation[2])

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

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Salvar Mundo",
            defaultextension=".obj",
            filetypes=[("Arquivos OBJ", "*.obj"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            self.viewport.export_obj(filepath)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Carregar Mundo",
            filetypes=[("Arquivos OBJ", "*.obj"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            self.viewport.import_obj(filepath)
            self.update_list_box()