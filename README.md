# Sistema de Control de Asistencia y Detección de EPP con Reconocimiento Facial

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un sistema de escritorio desarrollado en Python para la gestión de asistencia de empleados y la verificación en tiempo real del uso correcto de Equipo de Protección Personal (EPP) mediante visión por computadora.

**Repositorio Principal:** [https://github.com/Suarezsh/Asistencia-deteccion-EPP/](https://github.com/Suarezsh/Asistencia-deteccion-EPP/)

---

## 🌟 Características Principales

- **Interfaz Gráfica Moderna:** Construida con `ttkbootstrap` para una apariencia limpia y profesional.
- **Dashboard Interactivo:** Visualiza estadísticas clave en tiempo real:
  - KPIs (Indicadores Clave de Rendimiento) como total de empleados, asistencias del día e incidentes de EPP.
  - Gráficos de asistencia de los últimos 7 días.
  - Gráfico de pastel sobre el cumplimiento de EPP.
- **Gestión de Empleados:** Funcionalidad completa para registrar, visualizar y eliminar empleados, almacenando sus fotografías en la base de datos para el reconocimiento facial.
- **Reconocimiento Facial:** Utiliza la biblioteca `face_recognition` para identificar a los empleados y marcar su asistencia de forma automática.
- **Detección de EPP con IA:**
  - Implementa un modelo YOLOv8 personalizado (`best.pt`) para la detección precisa de **cascos** y **chalecos**.
  - El sistema verifica si el empleado lleva el EPP requerido al momento de marcar su asistencia.
- **Base de Datos SQLite:** Sistema de base de datos ligero y sin necesidad de configuración para almacenar toda la información de empleados y registros de asistencia.
- **Reportes Detallados:** Un panel dedicado para visualizar el historial completo de asistencias, incluyendo el estado del EPP de cada registro.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3
- **Interfaz Gráfica:** `ttkbootstrap`
- **Visión por Computadora:** `opencv-python`
- **Reconocimiento Facial:** `face_recognition`
- **Detección de Objetos:** `ultralytics` (YOLOv8)
- **Visualización de Datos:** `matplotlib`
- **Base de Datos:** SQLite 3

---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### Prerrequisitos

- Tener Python 3.8 o superior instalado.
- Tener `pip` (el gestor de paquetes de Python) disponible en la línea de comandos.

### Pasos

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/Suarezsh/Asistencia-deteccion-EPP.git
    cd Asistencia-deteccion-EPP
    ```

2.  **Instala las dependencias:**
    El archivo `requirements.txt` contiene todas las bibliotecas necesarias. Instálalas con el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Verifica los modelos:**
    Asegúrate de que los modelos de IA (`best.pt` y `yolov8n.pt`) se encuentren en la carpeta raíz del proyecto.

---

## ▶️ Cómo Ejecutar la Aplicación

Una vez que hayas instalado las dependencias, puedes iniciar el sistema ejecutando el siguiente comando desde la carpeta raíz del proyecto:

```bash
python main.py
```

La aplicación se iniciará y la base de datos `asistencia.db` se creará automáticamente en la carpeta `base_de_datos/` si no existe.

---

## 📂 Estructura del Proyecto

```
.
├── best.pt               # Modelo YOLOv8 para EPP
├── yolov8n.pt            # Modelo YOLOv8 estándar
├── requirements.txt      # Dependencias del proyecto
├── main.py               # Punto de entrada de la aplicación
├── Detector.py           # Script de prueba para el modelo de EPP
├── README.md             # Este archivo
├── base_de_datos/        # Contiene la base de datos SQLite
├── conexion/             # Módulo para la conexión y operaciones con la BD
├── interfaz/             # Contiene todos los paneles de la GUI
├── logica/               # Lógica de negocio (controlador, reconocimiento)
└── ...
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles. Eres libre de usar, modificar y distribuir este software.

---

## ✍️ Autor

- **Suarezsh** - [Perfil de GitHub](https://github.com/Suarezsh)
