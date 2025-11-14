import face_recognition
import cv2
import numpy as np
from ultralytics import YOLO
from conexion.database import obtener_todos_los_empleados, obtener_foto_por_codigo
import io
from PIL import Image
import os

class ReconocimientoFacialEPP:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

        # Cargar el modelo YOLO 'best.pt'
        try:
            # Obtener la ruta base del script actual
            ruta_base = os.path.dirname(os.path.abspath(__file__))
            # Subir un nivel para encontrar best.pt en la raíz del proyecto
            ruta_modelo = os.path.join(ruta_base, '..', 'best.pt')
            self.yolo_model = YOLO(ruta_modelo)
        except Exception as e:
            print(f"Error al cargar 'best.pt': {e}. Asegúrate de que el archivo está en la carpeta raíz.")
            self.yolo_model = None

    def _preprocesar_frame(self, frame):
        """
        Preprocesa el frame para mejorar la detección, replicando la lógica de detector.py.
        """
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # suavizado = cv2.GaussianBlur(gris, (5, 5), 0) # detector.py usa GaussianBlur, pero CLAHE es más efectivo para contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        frame_mejorado = clahe.apply(gris)
        return cv2.cvtColor(frame_mejorado, cv2.COLOR_GRAY2BGR)

    def load_known_faces(self):
        empleados_data = obtener_todos_los_empleados()
        self.known_face_encodings = []
        self.known_face_names = []
        for empleado in empleados_data:
            codigo, nombre, apellidos = empleado[0], empleado[1], empleado[2]
            foto_blob = obtener_foto_por_codigo(codigo)
            if foto_blob:
                try:
                    img_data = io.BytesIO(foto_blob)
                    img_pil = Image.open(img_data)
                    img_np = np.array(img_pil.convert("RGB")) # Asegurar RGB para face_recognition
                    face_encodings = face_recognition.face_encodings(img_np)
                    if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(f"{nombre} {apellidos} ({codigo})")
                except Exception:
                    pass

    def reconocer_y_detectar(self, frame):
        """
        Realiza el reconocimiento facial y la detección de EPP usando 'best.pt'
        con el preprocesamiento correcto.
        """
        detecciones_epp = {'casco': False, 'chaleco': False, 'persona_detectada': False, 'nombre_reconocido': "Desconocido", 'codigo_reconocido': None}

        # --- Detección de EPP con best.pt ---
        if self.yolo_model:
            # Aplicar el preprocesamiento antes de la inferencia YOLO
            frame_preprocesado = self._preprocesar_frame(frame)
            results = self.yolo_model(frame_preprocesado, verbose=False, conf=0.5)[0] # Usar umbral de confianza de 0.5

            for r in results.boxes:
                x1, y1, x2, y2 = map(int, r.xyxy[0])
                cls_id = int(r.cls[0])
                label = self.yolo_model.names[cls_id]

                color = (255, 255, 255) # Blanco por defecto
                if label == 'casco':
                    detecciones_epp['casco'] = True
                    color = (0, 255, 0) # Verde
                elif label == 'chaleco':
                    detecciones_epp['chaleco'] = True
                    color = (255, 255, 0) # Amarillo/Cian
                elif label == 'humano':
                    detecciones_epp['persona_detectada'] = True
                    color = (0, 0, 255) # Rojo

                # Dibujar los resultados sobre el frame ORIGINAL
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Si se detecta casco, asumir que el chaleco también está presente (placeholder)
            if detecciones_epp['casco']:
                detecciones_epp['chaleco'] = True

        # --- Reconocimiento Facial ---
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Desconocido"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            if name != "Desconocido":
                detecciones_epp['nombre_reconocido'] = name.split(' (')[0]
                detecciones_epp['codigo_reconocido'] = name.split(' (')[1][:-1]

            top, right, bottom, left = [v * 4 for v in face_location]
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        return frame, detecciones_epp

    def recargar_caras_conocidas(self):
        """
        Vuelve a cargar las caras conocidas, útil si se añade un nuevo empleado.
        """
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
