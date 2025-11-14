from interfaz.panel_inicio import PanelInicio
from interfaz.panel_asistencia import PanelAsistencia
from interfaz.panel_registro import PanelRegistro
from interfaz.panel_reportes import PanelReportes
from interfaz.panel_inicio import PanelInicio
from interfaz.panel_asistencia import PanelAsistencia
from interfaz.panel_registro import PanelRegistro
from interfaz.panel_reportes import PanelReportes
from interfaz.panel_trabajadores import PanelTrabajadores
from conexion.database import agregar_empleado, eliminar_empleado_por_codigo, registrar_asistencia
from tkinter import messagebox
import cv2

class ControladorPrincipal:
    def __init__(self, app):
        self.app = app

    def mostrar_inicio(self):
        """ Muestra el panel de bienvenida. """
        if self.app:
            self.app.mostrar_panel(PanelInicio)

    def mostrar_asistencia(self):
        """ Muestra el panel principal de marcado de asistencia. """
        if self.app:
            self.app.mostrar_panel(PanelAsistencia)

    def mostrar_registro(self):
        """ Muestra el panel para registrar un nuevo empleado. """
        if self.app:
            self.app.mostrar_panel(PanelRegistro)

    def mostrar_reportes(self):
        """ Muestra el panel con los reportes de asistencia. """
        if self.app:
            self.app.mostrar_panel(PanelReportes)

    def mostrar_trabajadores(self):
        """ Muestra el panel con la lista de trabajadores. """
        if self.app:
            panel = self.app.paneles.get(PanelTrabajadores)
            if panel:
                panel.cargar_lista_empleados()
            self.app.mostrar_panel(PanelTrabajadores)

    def eliminar_empleado(self, codigo, nombre_completo):
        """ Pide confirmación y elimina un empleado. """
        confirmar = messagebox.askyesno(
            title="Confirmar Eliminación",
            message=f"¿Está seguro de que desea eliminar a '{nombre_completo}'?"
        )
        if confirmar:
            if eliminar_empleado_por_codigo(codigo):
                messagebox.showinfo("Éxito", "Empleado eliminado correctamente.")
                self.mostrar_trabajadores() # Recargar la lista
            else:
                messagebox.showerror("Error", "No se pudo eliminar al empleado.")

    def guardar_empleado(self, codigo, nombre, apellidos, foto_cv2):
        """ Valida y guarda un nuevo empleado. """
        if not all([codigo, nombre, apellidos, foto_cv2 is not None]):
            messagebox.showerror("Error", "Todos los campos y la foto son obligatorios.")
            return
        
        _, buffer = cv2.imencode('.PNG', foto_cv2)
        foto_blob = buffer.tobytes()

        if agregar_empleado(codigo, nombre, apellidos, foto_blob):
            messagebox.showinfo("Éxito", "Empleado registrado correctamente.")
            panel_registro = self.app.paneles.get(PanelRegistro)
            if panel_registro:
                panel_registro.reset_panel()
        else:
            messagebox.showerror("Error", "No se pudo registrar al empleado. El código podría existir.")

    def registrar_asistencia(self, codigo, tipo, casco_ok, chaleco_ok):
        """ Registra la asistencia de un empleado. """
        if registrar_asistencia(codigo, tipo, casco_ok, chaleco_ok):
            messagebox.showinfo("Éxito", f"Asistencia ({tipo}) registrada para {codigo}.")
        else:
            messagebox.showerror("Error", "No se pudo registrar la asistencia.")

