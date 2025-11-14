import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from conexion.database import obtener_reporte_asistencia

class PanelReportes(ttk.Frame):
    def __init__(self, parent, controlador): # Añadir 'controlador'
        super().__init__(parent, padding=20)
        self.parent = parent
        self.controlador = controlador # Guardar referencia si se necesita en el futuro
        
        # Título y Botón de Actualizar
        frame_titulo = ttk.Frame(self)
        frame_titulo.pack(fill=X, pady=(0, 20))
        
        titulo = ttk.Label(frame_titulo, text="Reporte de Asistencia", font=("Helvetica", 16, "bold"))
        titulo.pack(side=LEFT, expand=True)
        
        self.boton_actualizar = ttk.Button(frame_titulo, text="Actualizar", command=self.cargar_reporte, style="success-outline")
        self.boton_actualizar.pack(side=RIGHT)

        # Tabla de Reportes (Treeview)
        self.crear_tabla_reportes()
        
        # Cargar los datos iniciales
        self.cargar_reporte()

    def crear_tabla_reportes(self):
        frame_tabla = ttk.Frame(self)
        frame_tabla.pack(expand=True, fill=BOTH)

        # Columnas de la tabla
        columnas = ("codigo", "nombre", "apellidos", "fecha", "tipo", "casco", "chaleco")
        
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=15)

        # Definir encabezados
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("apellidos", text="Apellidos")
        self.tabla.heading("fecha", text="Fecha y Hora")
        self.tabla.heading("tipo", text="Tipo")
        self.tabla.heading("casco", text="Casco")
        self.tabla.heading("chaleco", text="Chaleco")

        # Definir ancho de columnas
        self.tabla.column("codigo", width=80, anchor=CENTER)
        self.tabla.column("nombre", width=150)
        self.tabla.column("apellidos", width=150)
        self.tabla.column("fecha", width=160, anchor=CENTER)
        self.tabla.column("tipo", width=80, anchor=CENTER)
        self.tabla.column("casco", width=70, anchor=CENTER)
        self.tabla.column("chaleco", width=70, anchor=CENTER)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient=VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tabla.pack(side=LEFT, expand=True, fill=BOTH)

    def cargar_reporte(self):
        # Limpiar tabla antes de cargar nuevos datos
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        # Obtener datos de la base de datos
        reporte_data = obtener_reporte_asistencia()
        
        # Insertar datos en la tabla
        for fila in reporte_data:
            # Convertir valores de casco/chaleco (0/1) a texto legible
            codigo, nombre, apellidos, fecha, tipo, casco_val, chaleco_val = fila
            
            casco_str = "Sí" if casco_val == 1 else "No"
            chaleco_str = "Sí" if chaleco_val == 1 else "No"
            
            # Formatear la fecha para que sea más legible
            fecha_formateada = fecha.split('.')[0] # Eliminar microsegundos
            
            valores_insertar = (codigo, nombre, apellidos, fecha_formateada, tipo.capitalize(), casco_str, chaleco_str)
            
            self.tabla.insert("", END, values=valores_insertar)
            
            # Aplicar etiquetas de color para el estado del EPP
            # (Esto requiere configurar tags, lo haremos simple por ahora)

# Para pruebas
if __name__ == '__main__':
    app = ttk.Window(themename="litera")
    app.title("Panel de Reportes de Prueba")
    panel = PanelReportes(app)
    panel.pack(expand=True, fill=BOTH)
    app.mainloop()