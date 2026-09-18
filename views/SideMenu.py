from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.Viewport import Viewport

import math
import tkinter as tk
from tkinter import filedialog

from data.Transform2d import Transform2d
from views.NewShapePopup import NewShapePopup

class SideMenu(tk.Frame):
    def __init__(self, parent, viewport: Viewport, **kwargs):
        super().__init__(parent, **kwargs)
        self.viewport = viewport

        #há um canvas aqui para habilitar scroll no menu lateral
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
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux (Scroll Up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux (Scroll Down)
        
        menu_frame = tk.LabelFrame(self.scrollable_frame, text="Menu de Funções", padx=5, pady=5)
        menu_frame.pack(fill="y", expand=True)
        
        # --- 1. Objetos ---
        tk.Label(menu_frame, text="Objetos").pack(anchor="w")
        
        self.listbox = tk.Listbox(menu_frame, height=5, selectbackground="#000080", selectforeground="white", exportselection=False)
        self.listbox.pack(fill="x", pady=(0, 5))
        self.update_list_box()

        tk.Button(menu_frame, text="Adicionar Objeto", command=self.open_create_new_shape).pack(fill="x", pady=(0, 5))
        
        # --- 2. Window (Câmera) ---
        window_frame = tk.LabelFrame(menu_frame, text="Window (Câmera)", padx=5, pady=5)
        window_frame.pack(fill="x", pady=2)
        
        frame_passo = tk.Frame(window_frame)
        frame_passo.pack(fill="x", pady=(0, 5))
        tk.Label(frame_passo, text="Passo:").pack(side="left")
        self.ent_passo = tk.Entry(frame_passo, width=5)
        self.ent_passo.insert(0, "10")
        self.ent_passo.pack(side="left", padx=2)
        tk.Label(frame_passo, text="%").pack(side="left")
        
        frame_nav = tk.Frame(window_frame)
        frame_nav.pack()
        tk.Button(frame_nav, command=self.move_viewport_up, text="Up", width=4).grid(row=0, column=1, pady=1)
        tk.Button(frame_nav, command=self.move_viewport_left, text="Left", width=4).grid(row=1, column=0, padx=1)
        tk.Button(frame_nav, command=self.move_viewport_right, text="Right", width=4).grid(row=1, column=2, padx=1)
        tk.Button(frame_nav, command=self.move_viewport_down, text="Down", width=4).grid(row=2, column=1, pady=1)
        tk.Button(frame_nav, command=self.zoom_viewport_in, text="In", width=4).grid(row=0, column=3, padx=(10, 0))
        tk.Button(frame_nav, command=self.zoom_viewport_out, text="Out", width=4).grid(row=2, column=3, padx=(10, 0))
        tk.Button(frame_nav, command=self.rotate_window_left, text="↶", width=4).grid(row=0, column=4, padx=(10, 0))
        tk.Button(frame_nav, command=self.rotate_window_right, text="↷", width=4).grid(row=2, column=4, padx=(10, 0))
        
        # --- 3. Translação (Objeto) ---
        trans_frame = tk.LabelFrame(menu_frame, text="Translação (Objeto)", padx=5, pady=5)
        trans_frame.pack(fill="x", pady=2)
        
        f_trans_inputs = tk.Frame(trans_frame)
        f_trans_inputs.pack(pady=2)
        tk.Label(f_trans_inputs, text="Dx:").grid(row=0, column=0)
        self.ent_dx = tk.Entry(f_trans_inputs, width=5)
        self.ent_dx.insert(0, "2.0")
        self.ent_dx.grid(row=0, column=1, padx=2)
        
        tk.Label(f_trans_inputs, text="Dy:").grid(row=0, column=2)
        self.ent_dy = tk.Entry(f_trans_inputs, width=5)
        self.ent_dy.insert(0, "2.0")
        self.ent_dy.grid(row=0, column=3, padx=2)
        
        tk.Button(trans_frame, text="Mover Objeto", command=self.transladar_objeto).pack(fill="x")

        # --- 4. Escalonamento (Objeto) ---
        esc_frame = tk.LabelFrame(menu_frame, text="Escalonamento (Objeto)", padx=5, pady=5)
        esc_frame.pack(fill="x", pady=2)
        
        f_esc_inputs = tk.Frame(esc_frame)
        f_esc_inputs.pack(pady=2)
        tk.Label(f_esc_inputs, text="Sx:").grid(row=0, column=0)
        self.ent_sx = tk.Entry(f_esc_inputs, width=5)
        self.ent_sx.insert(0, "1.5")
        self.ent_sx.grid(row=0, column=1, padx=2)
        
        tk.Label(f_esc_inputs, text="Sy:").grid(row=0, column=2)
        self.ent_sy = tk.Entry(f_esc_inputs, width=5)
        self.ent_sy.insert(0, "1.5")
        self.ent_sy.grid(row=0, column=3, padx=2)
        
        tk.Button(esc_frame, text="Escalar no Centro", command=self.escalonar_objeto).pack(fill="x")

        # --- 5. Rotação (Objeto) ---
        rot_frame = tk.LabelFrame(menu_frame, text="Rotação (Objeto)", padx=5, pady=5)
        rot_frame.pack(fill="x", pady=2)
        
        frame_graus = tk.Frame(rot_frame)
        frame_graus.pack(fill="x", pady=(0, 5))
        tk.Label(frame_graus, text="Graus:").pack(side="left")
        self.ent_graus = tk.Entry(frame_graus, width=5)
        self.ent_graus.insert(0, "45")
        self.ent_graus.pack(side="left", padx=2)
        tk.Label(frame_graus, text="º").pack(side="left")
        
        # Seleção do Pivô de Rotação
        self.var_tipo_rot = tk.StringVar(value="centro")
        tk.Radiobutton(rot_frame, text="Centro do Objeto", variable=self.var_tipo_rot, value="centro").pack(anchor="w")
        tk.Radiobutton(rot_frame, text="Origem do Mundo (0,0)", variable=self.var_tipo_rot, value="origem").pack(anchor="w")
        tk.Radiobutton(rot_frame, text="Ponto Arbitrário", variable=self.var_tipo_rot, value="arbitrario").pack(anchor="w")
        
        # Entradas para o Ponto Arbitrário (X e Y)
        frame_arb = tk.Frame(rot_frame)
        frame_arb.pack(fill="x", pady=(2, 5))
        tk.Label(frame_arb, text="X:").pack(side="left")
        self.ent_rot_x = tk.Entry(frame_arb, width=5)
        self.ent_rot_x.insert(0, "0")
        self.ent_rot_x.pack(side="left", padx=(2, 10))
        
        tk.Label(frame_arb, text="Y:").pack(side="left")
        self.ent_rot_y = tk.Entry(frame_arb, width=5)
        self.ent_rot_y.insert(0, "0")
        self.ent_rot_y.pack(side="left", padx=2)
        
        tk.Button(rot_frame, text="Aplicar Rotação", command=self.rotacionar_objeto).pack(fill="x", pady=2)
        
        tk.Button(menu_frame, text="Resetar Câmera", command=self.reset_camera).pack(fill="x", padx=10, pady=10)

        # --- Selecao de algoritmo de clipping ---
        clip_frame = tk.LabelFrame(menu_frame, text="Algoritmo de Clipping de Linha", padx=5, pady=5)
        clip_frame.pack(fill="x", pady=2)

        self.var_tipo_clip = tk.StringVar(value="liang-barsky")
        tk.Radiobutton(clip_frame, text="Liang-Barsky", variable=self.var_tipo_clip, value="liang-barsky", command=self.set_clipping_algorithm).pack(anchor="w")
        tk.Radiobutton(clip_frame, text="Cohen-Sutherland", variable=self.var_tipo_clip, value="cohen-sutherland", command=self.set_clipping_algorithm).pack(anchor="w")

        file_frame = tk.LabelFrame(menu_frame, text="Arquivos", padx=5, pady=5)
        file_frame.pack(fill="x", pady=10)
        
        tk.Button(file_frame, text="Salvar", command=self.save_file).pack(fill="x", pady=1)
        tk.Button(file_frame, text="Carregar", command=self.load_file).pack(fill="x", pady=1)

    def open_create_new_shape(self):
        NewShapePopup(self.winfo_toplevel(), self.viewport, self.update_list_box)

    def _on_mousewheel(self, event):
        """Permite rolar o menu usando a rodinha do mouse."""
        # Linux usa Button-4 (Cima) e Button-5 (Baixo)
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def update_list_box(self):
        self.listbox.delete(0, tk.END)
        for i, shape in enumerate(self.viewport.shapes):
            nome = getattr(shape, 'name', f"Objeto {i}")
            self.listbox.insert(tk.END, nome)
            
        if self.viewport.shapes:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(tk.END)
        
    def _get_selected_shape(self):
        """Retorna o objeto atualmente selecionado na Listbox."""
        selecao = self.listbox.curselection()
        if not selecao:
            return None
        return self.viewport.shapes[selecao[0]]

    def transladar_objeto(self):
        shape = self._get_selected_shape()
        if not shape: return
        try:
            dx = float(self.ent_dx.get())
            dy = float(self.ent_dy.get())
            
            Transform2d().translation(dx, dy).apply(shape)
            self.viewport.render()
        except ValueError:
            pass

    def escalonar_objeto(self):
        shape = self._get_selected_shape()
        if not shape: return
        try:
            sx = float(self.ent_sx.get())
            sy = float(self.ent_sy.get())
            
            # Escalonar a partir do centro para não arremessar o objeto pela tela
            cx, cy = shape.center()
            
            t = Transform2d()
            t.translation(-cx, -cy).escale(sx, sy).translation(cx, cy).apply(shape)
            self.viewport.render()
        except ValueError:
            pass

    def rotacionar_objeto(self):
        shape = self._get_selected_shape()
        if not shape: return
        try:
            angulo = float(self.ent_graus.get())
            tipo_pivo = self.var_tipo_rot.get()
            
            t = Transform2d()
            
            if tipo_pivo == "centro":
                cx, cy = shape.center()
                t.translation(-cx, -cy).rotation(angulo).translation(cx, cy)
                
            elif tipo_pivo == "origem":
                t.rotation(angulo)
                
            elif tipo_pivo == "arbitrario":
                px = float(self.ent_rot_x.get())
                py = float(self.ent_rot_y.get())
                t.translation(-px, -py).rotation(angulo).translation(px, py)
            
            t.apply(shape)
            self.viewport.render()
            
        except ValueError:
            pass


    def reset_camera(self):
        # Exemplo de reset caso precise
        self.viewport.wData.x_min, self.viewport.wData.y_min = -100, -100
        self.viewport.wData.x_max, self.viewport.wData.y_max = 100, 100
        self.viewport.wData.angle = 0.0
        self.viewport.render()

    def move_camera(self, dx_local: float, dy_local: float):
        rad = math.radians(-self.viewport.wData.angle)

        # Correção de ângulo
        dx_mundo = dx_local * math.cos(rad) - dy_local * math.sin(rad)
        dy_mundo = dx_local * math.sin(rad) + dy_local * math.cos(rad)
        
        self.viewport.pan(dx_mundo, dy_mundo)

    def move_viewport_left(self):
        passo = float(self.ent_passo.get()) / 100.0
        dx = self.viewport.wData.width() * passo
        self.move_camera(-dx, 0)

    def move_viewport_right(self):
        passo = float(self.ent_passo.get()) / 100.0
        dx = self.viewport.wData.width() * passo
        self.move_camera(dx, 0)

    def move_viewport_up(self):
        passo = float(self.ent_passo.get()) / 100.0
        dy = self.viewport.wData.height() * passo
        self.move_camera(0, dy)

    def move_viewport_down(self):
        passo = float(self.ent_passo.get()) / 100.0
        dy = self.viewport.wData.height() * passo
        self.move_camera(0, -dy)

    def zoom_viewport_in(self):
        passo = float(self.ent_passo.get()) / 100.0
        factor = 1.0 - passo
        if factor > 0:
            self.viewport.zoom(factor)

    def zoom_viewport_out(self):
        passo = float(self.ent_passo.get()) / 100.0
        factor = 1.0 + passo
        self.viewport.zoom(factor)

    def rotate_window_left(self):
        passo = float(self.ent_passo.get())
        self.viewport.rotate(passo)

    def rotate_window_right(self):
        passo = float(self.ent_passo.get())
        self.viewport.rotate(-passo)

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