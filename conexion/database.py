import sqlite3
import os

# --- Configuración de la Base de Datos ---
DB_FOLDER = 'base_de_datos'
DB_NAME = 'asistencia.db'
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def crear_tablas_iniciales():
    """
    Crea las tablas 'empleados' y 'asistencia' en la base de datos
    si estas no existen. Esta función es segura de ejecutar múltiples veces.
    """
    # Asegurarse de que la carpeta de la base de datos exista
    os.makedirs(DB_FOLDER, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # --- Tabla de Empleados ---
        # Almacena la información permanente de cada empleado.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                codigo TEXT(8) PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                foto BLOB NOT NULL
            )
        """)

        # --- Tabla de Asistencia ---
        # Almacena cada evento de entrada o salida.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empleado_codigo TEXT(8) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'salida')),
                casco INTEGER NOT NULL CHECK(casco IN (0, 1)),
                chaleco INTEGER NOT NULL CHECK(chaleco IN (0, 1)),
                FOREIGN KEY (empleado_codigo) REFERENCES empleados (codigo) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Base de datos y tablas verificadas/creadas correctamente.")

    except sqlite3.Error as e:
        print(f"Error al crear/verificar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def agregar_empleado(codigo, nombre, apellidos, foto_blob):
    """
    Agrega un nuevo empleado a la base de datos.
    Retorna True si fue exitoso, False si ocurrió un error (ej. código duplicado).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO empleados (codigo, nombre, apellidos, foto) VALUES (?, ?, ?, ?)",
            (codigo, nombre, apellidos, foto_blob)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Este error ocurre si el 'codigo' (PRIMARY KEY) ya existe.
        print(f"Error: El código de empleado '{codigo}' ya existe.")
        return False
    except sqlite3.Error as e:
        print(f"Error al agregar empleado: {e}")
        return False
    finally:
        if conn:
            conn.close()

def eliminar_empleado_por_codigo(codigo):
    """
    Elimina un empleado y todos sus registros de asistencia de la base de datos.
    Retorna True si fue exitoso, False si no.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Gracias a ON DELETE CASCADE, los registros de asistencia se borrarán automáticamente.
        cursor.execute("DELETE FROM empleados WHERE codigo = ?", (codigo,))
        conn.commit()
        # Verificar si la eliminación tuvo efecto
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error al eliminar empleado: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_todos_los_empleados():
    """
    Recupera una lista de todos los empleados (código, nombre, apellidos).
    Retorna una lista de tuplas.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, apellidos FROM empleados ORDER BY apellidos, nombre")
        empleados = cursor.fetchall()
        return empleados
    except sqlite3.Error as e:
        print(f"Error al obtener los empleados: {e}")
        return []
    finally:
        if conn:
            conn.close()

def obtener_foto_por_codigo(codigo):
    """
    Recupera la foto (BLOB) de un empleado específico por su código.
    Retorna el BLOB o None si no se encuentra.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT foto FROM empleados WHERE codigo = ?", (codigo,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"Error al obtener la foto: {e}")
        return None
    finally:
        if conn:
            conn.close()

def registrar_asistencia(empleado_codigo, tipo, casco_ok, chaleco_ok):
    """
    Registra un evento de asistencia para un empleado.
    `casco_ok` y `chaleco_ok` deben ser 0 (NO) o 1 (OK).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO asistencia (empleado_codigo, tipo, casco, chaleco) VALUES (?, ?, ?, ?)",
            (empleado_codigo, tipo, casco_ok, chaleco_ok)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al registrar asistencia: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_reporte_asistencia():
    """
    Obtiene todos los registros de asistencia, uniendo la información del empleado.
    Retorna una lista de tuplas con:
    (codigo, nombre, apellidos, timestamp, tipo, casco, chaleco)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.codigo,
                e.nombre,
                e.apellidos,
                a.timestamp,
                a.tipo,
                a.casco,
                a.chaleco
            FROM asistencia a
            JOIN empleados e ON a.empleado_codigo = e.codigo
            ORDER BY a.timestamp DESC
        """)
        reporte = cursor.fetchall()
        return reporte
    except sqlite3.Error as e:
        print(f"Error al obtener el reporte de asistencia: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Funciones para el Dashboard ---

def contar_total_empleados():
    """Cuenta el número total de empleados registrados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(codigo) FROM empleados")
        total = cursor.fetchone()[0]
        return total
    except sqlite3.Error as e:
        print(f"Error al contar empleados: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def contar_asistencias_hoy():
    """Cuenta cuántos empleados únicos han marcado 'entrada' hoy."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT empleado_codigo) 
            FROM asistencia 
            WHERE DATE(timestamp) = DATE('now', 'localtime') AND tipo = 'entrada'
        """)
        total = cursor.fetchone()[0]
        return total
    except sqlite3.Error as e:
        print(f"Error al contar asistencias de hoy: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def contar_incidentes_epp_hoy():
    """Cuenta los registros de 'entrada' de hoy donde faltó casco o chaleco."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(id) 
            FROM asistencia 
            WHERE DATE(timestamp) = DATE('now', 'localtime') 
            AND tipo = 'entrada' 
            AND (casco = 0 OR chaleco = 0)
        """)
        total = cursor.fetchone()[0]
        return total
    except sqlite3.Error as e:
        print(f"Error al contar incidentes de EPP de hoy: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def obtener_asistencia_ultimos_7_dias():
    """Recupera el conteo de asistencias únicas por día de los últimos 7 días."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d', timestamp) as dia,
                COUNT(DISTINCT empleado_codigo) as total_asistencias
            FROM asistencia
            WHERE DATE(timestamp) >= DATE('now', '-6 days', 'localtime') AND tipo = 'entrada'
            GROUP BY dia
            ORDER BY dia ASC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error al obtener asistencia de los últimos 7 días: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Si se ejecuta este archivo directamente, crea la base de datos.
    crear_tablas_iniciales()
