from interfaz.ventana_principal import VentanaPrincipal
from logica.controlador_principal import ControladorPrincipal
from conexion.database import crear_tablas_iniciales

def main():
    """
    Función principal para iniciar la aplicación.
    """
    # 1. Asegurarse de que la base de datos y las tablas existan.
    crear_tablas_iniciales()

    # 2. Crear el controlador
    controlador = ControladorPrincipal(None) 
    
    # 3. Crear la vista (la ventana principal) y pasarle el controlador
    app = VentanaPrincipal(controlador)
    
    # 4. Asignar la vista al controlador
    controlador.app = app
    
    # 5. Mostrar el panel de bienvenida inicial
    controlador.mostrar_inicio()
    
    # 6. Iniciar el bucle principal de la aplicación
    app.mainloop()

if __name__ == '__main__':
    main()
