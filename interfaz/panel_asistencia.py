import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import cv2
from PIL import Image, ImageTk
import threading
import time
from logica.reconocimiento import ReconocimientoFacialEPP
from tkinter import messagebox

class PanelAsistencia(ttk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        self.reconocimiento_epp = ReconocimientoFacialEPP()
        
        self.hilo_camara = None
        self.camara_activa = False
        self.cap = None
        self.latest_frame = None
        self.latest_detections = None

        self._crear_layout()
        # NO iniciar la cámara en el constructor
        self.bind("<Destroy>", self._liberar_recursos)

    def activate(self):
        """Activa el panel: recarga caras y enciende la cámara."""
        print("Activando panel de asistencia...")
        self.reconocimiento_epp.recargar_caras_conocidas()
        self.iniciar_camara()

    def deactivate(self):
        """Desactiva el panel: apaga la cámara."""
        print("Desactivando panel de asistencia...")
        self._liberar_recursos()

    def _crear_layout(self):
        # ... (El layout no cambia, solo la lógica de actualización)
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        form_frame = ttk.Frame(main_frame, padding=20)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        form_frame.columnconfigure(1, weight=1)

        header = ttk.Label(form_frame, text="Marcar Asistencia", font=("Helvetica", 22, "bold"), bootstyle=PRIMARY)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 30), sticky="w")

        campos = {
            "Código Empleado:": "var_codigo", 
            "Nombre Completo:": "var_nombre_completo", 
            "Casco:": "var_casco", 
            "Chaleco:": "var_chaleco",
            "Tipo de Registro:": "var_tipo_registro"
        }
        self.vars = {}
        for i, (texto, var_name) in enumerate(campos.items(), start=1):
            ttk.Label(form_frame, text=texto, font=("Helvetica", 12)).grid(row=i, column=0, sticky="w", pady=10)
            if var_name == "var_tipo_registro":
                self.vars[var_name] = ttk.StringVar(value="entrada")
                radio_entrada = ttk.Radiobutton(form_frame, text="Entrada", variable=self.vars[var_name], value="entrada", bootstyle="success-round-toggle")
                radio_entrada.grid(row=i, column=1, sticky="w", padx=5)
                radio_salida = ttk.Radiobutton(form_frame, text="Salida", variable=self.vars[var_name], value="salida", bootstyle="danger-round-toggle")
                radio_salida.grid(row=i, column=1, sticky="e", padx=5)
            else:
                self.vars[var_name] = ttk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=self.vars[var_name], font=("Helvetica", 12), state=READONLY)
                entry.grid(row=i, column=1, sticky="ew", padx=5)

        self.btn_marcar_asistencia = ttk.Button(
            form_frame, 
            text="Marcar Asistencia", 
            bootstyle=SUCCESS, 
            command=self._marcar_asistencia,
            state=DISABLED
        )
        self.btn_marcar_asistencia.grid(row=len(campos)+2, column=0, columnspan=2, pady=(40, 0), sticky="ew")

        cam_frame = ttk.Frame(main_frame, padding=20)
        cam_frame.grid(row=0, column=1, sticky="nsew")
        cam_frame.rowconfigure(0, weight=1)
        cam_frame.columnconfigure(0, weight=1)

        self.label_camara = ttk.Label(cam_frame, text="Iniciando Cámara...", anchor=CENTER, background="#2b2b2b")
        self.label_camara.grid(row=0, column=0, sticky="nsew")

    def iniciar_camara(self):
        if not self.camara_activa:
            self.camara_activa = True
            self.hilo_camara = threading.Thread(target=self._video_loop, daemon=True)
            self.hilo_camara.start()
            # Iniciar el bucle de actualización de la UI
            self.after(100, self._update_ui_loop)

    def _video_loop(self):
        """Bucle de video que se ejecuta en un hilo separado."""
        self.cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara.") # This should appear in the console if it fails.
            self.camara_activa = False
            return

        while self.camara_activa:
            ret, frame = self.cap.read()
            if ret:
                # Procesar el frame y guardar los resultados
                self.latest_frame, self.latest_detections = self.reconocimiento_epp.reconocer_y_detectar(frame)
            else:
                # Si no se puede leer el frame, esperar un poco
                time.sleep(0.1)
        
        if self.cap.isOpened():
            self.cap.release()

    def _update_ui_loop(self):
        """Bucle que se ejecuta en el hilo principal para actualizar la UI."""
        if self.latest_frame is not None:
            self._mostrar_frame_en_label(self.latest_frame)
            self._actualizar_estado_deteccion(self.latest_detections)
        
        if self.camara_activa:
            self.after(30, self._update_ui_loop) # Repetir cada ~30ms

    def _mostrar_frame_en_label(self, frame_cv2):
        frame_rgb = cv2.cvtColor(frame_cv2, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        w, h = self.label_camara.winfo_width(), self.label_camara.winfo_height()
        if w > 1 and h > 1:
            img.thumbnail((w, h), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image=img)
        self.label_camara.config(image=photo)
        self.label_camara.image = photo

    def _actualizar_estado_deteccion(self, detecciones):
        if not detecciones: return

        codigo_reconocido = detecciones.get('codigo_reconocido', None)
        casco_detectado = detecciones['casco']
        chaleco_detectado = detecciones['chaleco']

        self.vars['var_codigo'].set(codigo_reconocido if codigo_reconocido else "")
        self.vars['var_nombre_completo'].set(detecciones.get('nombre_reconocido', "Desconocido") if codigo_reconocido else "")
        self.vars['var_casco'].set("OK" if casco_detectado else "NO")
        self.vars['var_chaleco'].set("OK" if chaleco_detectado else "NO")

        if codigo_reconocido and casco_detectado and chaleco_detectado:
            self.btn_marcar_asistencia.config(state=NORMAL)
        else:
            self.btn_marcar_asistencia.config(state=DISABLED)

    def _marcar_asistencia(self):
        codigo = self.vars['var_codigo'].get()
        if codigo:
            tipo = self.vars['var_tipo_registro'].get()
            casco = 1 if self.vars['var_casco'].get() == "OK" else 0
            chaleco = 1 if self.vars['var_chaleco'].get() == "OK" else 0
            
            self.controlador.registrar_asistencia(codigo, tipo, casco, chaleco)
            self.reset_panel()
        else:
            messagebox.showwarning("Advertencia", "No hay un empleado reconocido.")

    def reset_panel(self):
        self.latest_frame = None
        self.latest_detections = None
        self.vars['var_codigo'].set("")
        self.vars['var_nombre_completo'].set("")
        self.vars['var_casco'].set("")
        self.vars['var_chaleco'].set("")
        self.vars['var_tipo_registro'].set("entrada")
        self.btn_marcar_asistencia.config(state=DISABLED)

    def _liberar_recursos(self, event=None):
        self.camara_activa = False
        if self.hilo_camara and self.hilo_camara.is_alive():
            self.hilo_camara.join(timeout=1)
