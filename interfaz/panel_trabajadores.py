import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from conexion.database import obtener_todos_los_empleados, obtener_foto_por_codigo
from PIL import Image, ImageTk
import io

class PanelTrabajadores(ttk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        self._crear_widgets()
        self.cargar_lista_empleados()

    def _crear_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill=BOTH)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(1, weight=1) # Columna de la foto se expande

        header = ttk.Label(main_frame, text="Lista de Trabajadores", font=("Helvetica", 24, "bold"), bootstyle=PRIMARY)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # --- Columna Izquierda: Lista de Empleados ---
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        list_frame.rowconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "apellidos")
        self.tree = ttk.Treeview(list_frame, columns=columnas, show="headings", bootstyle=PRIMARY)
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellidos", text="Apellidos")
        self.tree.column("codigo", width=100)
        self.tree.column("nombre", width=150)
        self.tree.column("apellidos", width=150)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_empleado_seleccionado)

        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Botón de Eliminar
        self.btn_eliminar = ttk.Button(list_frame, text="Eliminar Empleado", bootstyle=DANGER, state=DISABLED, command=self._solicitar_eliminacion)
        self.btn_eliminar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # --- Columna Derecha: Visor de Foto ---
        photo_frame = ttk.Labelframe(main_frame, text="Foto del Empleado", padding=10)
        photo_frame.grid(row=1, column=1, sticky="nsew")
        photo_frame.rowconfigure(0, weight=1)
        photo_frame.columnconfigure(0, weight=1)

        self.label_foto = ttk.Label(photo_frame, text="Seleccione un empleado\nde la lista", anchor=CENTER, font=("Helvetica", 14))
        self.label_foto.grid(row=0, column=0, sticky="nsew")

    def cargar_lista_empleados(self):
        # Limpiar lista anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar nuevos datos
        empleados = obtener_todos_los_empleados()
        for i, empleado in enumerate(empleados):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", END, values=empleado, tags=(tag,))
        
        self.tree.tag_configure('evenrow', background='#f0f0f0')
        self.tree.tag_configure('oddrow', background='white')
        # Desactivar el botón por si acaso
        self.btn_eliminar.config(state=DISABLED)
        self.label_foto.config(image=None, text="Seleccione un empleado\nde la lista")

    def on_empleado_seleccionado(self, event=None):
        if self.tree.selection():
            self.btn_eliminar.config(state=NORMAL)
            self.mostrar_foto_seleccionada()
        else:
            # Si no hay selección, desactivar el botón y limpiar la foto
            self.btn_eliminar.config(state=DISABLED)
            self.label_foto.config(image=None, text="Seleccione un empleado\nde la lista")

    def mostrar_foto_seleccionada(self, event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            # Esto ya se maneja en on_empleado_seleccionado, pero es una buena redundancia
            self.label_foto.config(image=None, text="Seleccione un empleado\nde la lista")
            return

        item = self.tree.item(seleccion[0])
        codigo_empleado = item['values'][0]
        
        foto_blob = obtener_foto_por_codigo(codigo_empleado)

        if foto_blob:
            try:
                # Convertir el BLOB a una imagen que Tkinter pueda mostrar
                img_data = io.BytesIO(foto_blob)
                img = Image.open(img_data)

                w, h = self.label_foto.winfo_width(), self.label_foto.winfo_height()
                if w > 1 and h > 1:
                    img.thumbnail((w - 20, h - 20), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)
                self.label_foto.config(image=photo, text="")
                self.label_foto.image = photo
            except Exception as e:
                self.label_foto.config(image=None, text=f"Error al cargar\nla imagen: {e}")
        else:
            self.label_foto.config(image=None, text="No se encontró\nfoto para este empleado")

    def _solicitar_eliminacion(self):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        codigo = item['values'][0]
        nombre_completo = f"{item['values'][1]} {item['values'][2]}"
        
        self.controlador.eliminar_empleado(codigo, nombre_completo)
