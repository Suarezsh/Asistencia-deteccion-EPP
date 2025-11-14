import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import cv2
from PIL import Image, ImageTk
import threading
import time
from tkinter import filedialog
import numpy as np

class PanelRegistro(ttk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        
        self.hilo_camara = None
        self.camara_activa = False
        self.cap = None
        self.latest_frame_cv2 = None
        self.foto_capturada = None

        self._crear_layout()
        # NO iniciar la cámara en el constructor
        self.bind("<Destroy>", self._liberar_recursos)

    def activate(self):
        """Activa el panel: enciende la cámara."""
        print("Activando panel de registro...")
        self.iniciar_camara()

    def deactivate(self):
        """Desactiva el panel: apaga la cámara."""
        print("Desactivando panel de registro...")
        self._liberar_recursos()

    def _crear_layout(self):
        # ... (El layout no cambia)
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        form_frame = ttk.Frame(main_frame, padding=20)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        form_frame.columnconfigure(1, weight=1)

        header = ttk.Label(form_frame, text="Registrar Empleado", font=("Helvetica", 22, "bold"), bootstyle=SUCCESS)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky="w")

        campos = {"ID Empleado (8 dígitos):": "entry_id", "Nombres:": "entry_nombres", "Apellidos:": "entry_apellidos"}
        for i, (texto, var_name) in enumerate(campos.items(), start=1):
            ttk.Label(form_frame, text=texto, font=("Helvetica", 12)).grid(row=i, column=0, sticky="w", pady=10)
            entry = ttk.Entry(form_frame, font=("Helvetica", 12))
            entry.grid(row=i, column=1, sticky="ew", padx=5)
            setattr(self, var_name, entry)

        cam_frame = ttk.Frame(main_frame, padding=20)
        cam_frame.grid(row=0, column=1, sticky="nsew")
        cam_frame.rowconfigure(0, weight=1)
        cam_frame.columnconfigure(0, weight=1)

        self.label_camara = ttk.Label(cam_frame, text="Iniciando Cámara...", anchor=CENTER, background="#2b2b2b")
        self.label_camara.grid(row=0, column=0, sticky="nsew")

        cam_button_frame = ttk.Frame(cam_frame)
        cam_button_frame.grid(row=1, column=0, pady=10, sticky="ew")
        cam_button_frame.columnconfigure((0, 1), weight=1)

        self.btn_tomar_foto = ttk.Button(cam_button_frame, text="Tomar Foto", bootstyle=PRIMARY, command=self._tomar_foto)
        self.btn_tomar_foto.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_subir_foto = ttk.Button(cam_button_frame, text="Subir Foto", bootstyle=INFO, command=self._subir_foto)
        self.btn_subir_foto.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        button_container = ttk.Frame(form_frame)
        button_container.grid(row=len(campos)+2, column=0, columnspan=2, sticky="se", pady=(40,0))
        form_frame.rowconfigure(len(campos)+1, weight=1)

        self.btn_guardar = ttk.Button(button_container, text="Agregar Trabajador", bootstyle=SUCCESS, command=self._guardar_empleado)
        self.btn_guardar.pack(side=RIGHT, padx=5)
        
        self.btn_cancelar = ttk.Button(button_container, text="Cancelar", bootstyle=(SECONDARY, OUTLINE), command=self.controlador.mostrar_inicio)
        self.btn_cancelar.pack(side=RIGHT)

    def iniciar_camara(self):
        if not self.camara_activa:
            self.camara_activa = True
            self.hilo_camara = threading.Thread(target=self._video_loop, daemon=True)
            self.hilo_camara.start()
            self.after(100, self._update_ui_loop)

    def _video_loop(self):
        """Bucle de video en hilo separado."""
        self.cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            self.camara_activa = False
            return

        while self.camara_activa:
            ret, frame = self.cap.read()
            if ret:
                self.latest_frame_cv2 = frame
            else:
                time.sleep(0.1)
        
        if self.cap.isOpened():
            self.cap.release()

    def _update_ui_loop(self):
        """Actualiza la UI en el hilo principal."""
        if self.camara_activa and self.latest_frame_cv2 is not None:
            self._mostrar_frame_en_label(self.latest_frame_cv2)
        
        if self.winfo_exists(): # Prevenir errores si el widget es destruido
            self.after(30, self._update_ui_loop)

    def _mostrar_frame_en_label(self, frame_cv2):
        frame_rgb = cv2.cvtColor(frame_cv2, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        w, h = self.label_camara.winfo_width(), self.label_camara.winfo_height()
        if w > 1 and h > 1:
            img.thumbnail((w, h), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image=img)
        self.label_camara.config(image=photo)
        self.label_camara.image = photo

    def _tomar_foto(self):
        if self.latest_frame_cv2 is not None:
            self.foto_capturada = self.latest_frame_cv2.copy()
            self.camara_activa = False # Detiene el bucle de video
            self._mostrar_frame_en_label(self.foto_capturada) # Muestra la foto estática
            self.btn_tomar_foto.config(text="Volver a Tomar", bootstyle=WARNING, command=self._reset_camara)
            self.btn_subir_foto.config(state=DISABLED)

    def _subir_foto(self):
        filepath = filedialog.askopenfilename(filetypes=(("Archivos de imagen", "*.png *.jpg *.jpeg"),))
        if not filepath: return

        self.camara_activa = False
        try:
            img_pil = Image.open(filepath)
            self.foto_capturada = cv2.cvtColor(np.array(img_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
            self._mostrar_frame_en_label(self.foto_capturada)
            self.btn_tomar_foto.config(text="Volver a Tomar", bootstyle=WARNING, command=self._reset_camara)
            self.btn_subir_foto.config(state=NORMAL)
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar la imagen.\nError: {e}")

    def _reset_camara(self):
        self.foto_capturada = None
        self.latest_frame_cv2 = None
        self.btn_tomar_foto.config(text="Tomar Foto", bootstyle=PRIMARY, command=self._tomar_foto)
        self.btn_subir_foto.config(state=NORMAL)
        self.label_camara.config(image=None, text="Iniciando Cámara...")
        self.iniciar_camara()

    def _guardar_empleado(self):
        codigo = self.entry_id.get()
        nombre = self.entry_nombres.get()
        apellidos = self.entry_apellidos.get()
        self.controlador.guardar_empleado(codigo, nombre, apellidos, self.foto_capturada)

    def reset_panel(self):
        self.entry_id.delete(0, END)
        self.entry_nombres.delete(0, END)
        self.entry_apellidos.delete(0, END)
        self._reset_camara()

    def _liberar_recursos(self, event=None):
        self.camara_activa = False
        if self.hilo_camara and self.hilo_camara.is_alive():
            self.hilo_camara.join(timeout=1)
