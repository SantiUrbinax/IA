import cv2
import mediapipe as mp
import math

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def distancia (p1, p2):
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

# Funcion para determinar si un dedo esta levantado
def dedos_levantados(landmarks, umbral=0.1):
    # Comparar la posicion "y" del punto a la punta con los puntos anteriores
    dedos = {
        'Pulgar': False,
        'Indice': False,
        'Medio': False,
        'Anular': False,
        'Menique': False,
    }

    # Pulgar (comparacion en eje x para mejor precision)
    dedos['Pulgar'] = landmarks[4].x < landmarks[3].x if landmarks[0].x < landmarks[9].x else landmarks[4].x < landmarks[3].x

    dedos['Indice'] = landmarks[8].y < landmarks[6].y
    dedos['Medio'] = landmarks[12].y < landmarks[10].y
    dedos['Anular'] = landmarks[16].y < landmarks[14].y
    dedos['Menique'] = landmarks[20].y < landmarks[18].y

    return dedos

def detectar_gesto(dedos):
    # Gestos predefinidos
    if dedos['Indice'] and dedos['Medio'] and not any([dedos['Pulgar'], dedos['Anular'], dedos['Menique']]):
        return 'Victoria ✌️'
    elif dedos['Pulgar'] and not any([dedos['Indice'], dedos['Medio'], dedos['Anular'], dedos['Menique']]):
        return 'Pulgar Arriba 👍'
    elif any([dedos['Indice'], dedos['Pulgar']]) and distancia(landmarks[4], landmarks[8]) < 0.1:
        return 'ok 👌'
    elif all(dedos.values()):
        return 'Mano Abierta ✋'
    elif not any(dedos.values()):
        return 'Mano Cerrada ✊'
    else:
        return 'Gestos no reconocidos'

# Configurar la captura de la webcam
cap = cv2.VideoCapture(0) # 0 para la camara predeterminada

with mp_hands.Hands(static_image_mode = True, max_num_hands = 2, min_detection_confidence = 0.7, min_tracking_confidence = 0.7) as hands:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("No se pudo capturar la imagen")
            continue

        image = cv2.flip(image,1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hands_landmarks in results.multi_hand_landmarks:
                # Dibujar las marcas y conexiones
                mp_drawing.draw_landmarks(image, hands_landmarks, mp_hands.HAND_CONNECTIONS)
                # Obtener las marcas como una lista
                landmarks = hands_landmarks.landmark

                # Indices de los dedos segun mediaPipe
                dedos = dedos_levantados(landmarks)
                gesto = detectar_gesto(dedos)

                # Mostrar los dedos levantados en la imagen (opcional)
                info_dedos = f'Dedos: {[k for k, v in dedos.items() if v]}'
                cv2.putText(image, info_dedos, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 255, 0), 2)

                # Mostrar gesto detectado
                cv2.putText(image, f'Gesto: {gesto}', (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow('Deteccion de Gestos', image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()