import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Importar los nuevos paneles
from interfaz.panel_inicio import PanelInicio
from interfaz.panel_asistencia import PanelAsistencia
from interfaz.panel_registro import PanelRegistro
from interfaz.panel_reportes import PanelReportes
from interfaz.panel_trabajadores import PanelTrabajadores

class VentanaPrincipal(ttk.Window):

    def __init__(self, controlador):

        super().__init__(themename="litera")

        self.title("Sistema de Control de Asistencia y EPP")

        self.geometry("1024x768")

        self.minsize(900, 700)

        

        self.controlador = controlador

        self.paneles = {}

        self.current_panel = None



        # Contenedor principal para los paneles

        self.container = ttk.Frame(self)

        self.container.pack(expand=True, fill=BOTH)

        self.container.grid_rowconfigure(0, weight=1)

        self.container.grid_columnconfigure(0, weight=1)



        self._crear_menu()

        

    def _crear_menu(self):

        menu_bar = ttk.Menu(self)

        self.config(menu=menu_bar)



        # ... (el resto del menú no cambia)

        menu_archivo = ttk.Menu(menu_bar, tearoff=False)

        menu_bar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_archivo.add_command(label="Salir", command=self.quit)



        menu_opciones = ttk.Menu(menu_bar, tearoff=False)

        menu_bar.add_cascade(label="Opciones", menu=menu_opciones)

        menu_opciones.add_command(label="Inicio", command=self.controlador.mostrar_inicio)

        menu_opciones.add_separator()

        menu_opciones.add_command(label="Marcar Asistencia", command=self.controlador.mostrar_asistencia)

        menu_opciones.add_command(label="Registrar Empleado", command=self.controlador.mostrar_registro)

        menu_opciones.add_command(label="Ver Trabajadores", command=self.controlador.mostrar_trabajadores)

        menu_opciones.add_separator()

        menu_opciones.add_command(label="Ver Reportes", command=self.controlador.mostrar_reportes)



    def mostrar_panel(self, panel_class):

        """

        Muestra el panel solicitado. Lo crea si es la primera vez.

        Gestiona la activación/desactivación de paneles con cámara.

        """

        # Desactivar el panel actual si tiene un método deactivate

        if self.current_panel and hasattr(self.current_panel, 'deactivate'):

            self.current_panel.deactivate()



        # Comprobar si el panel ya ha sido creado

        if panel_class not in self.paneles:

            # Si no, crearlo y guardarlo

            panel = panel_class(self.container, self.controlador)

            self.paneles[panel_class] = panel

            panel.grid(row=0, column=0, sticky="nsew")

        

        # Obtener el panel a mostrar

        panel_to_show = self.paneles[panel_class]

        

        # Traerlo al frente

        panel_to_show.tkraise()

        

        # Activar el nuevo panel si tiene un método activate

        if hasattr(panel_to_show, 'activate'):

            panel_to_show.activate()

            

        self.current_panel = panel_to_show


