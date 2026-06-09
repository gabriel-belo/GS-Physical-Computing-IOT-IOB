import cv2
import numpy as np

def nothing(x):
    pass

video = cv2.VideoCapture('queimadas2.mp4')


cv2.namedWindow("Calibragem")
cv2.createTrackbar("Area Min",    "Calibragem", 500,  50000, nothing)
cv2.createTrackbar("Solidez Min", "Calibragem", 50,   100,   nothing)

def build_fire_mask(frame):
    """
    Combina três critérios para detectar fogo de forma robusta:
    1. Faixa HSV de chama (laranja/amarelo/vermelho)
    2. Núcleo branco/claro (alta luminosidade, baixa saturação)
    3. Dominância do canal vermelho no espaço BGR
    """
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv     = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # ── Critério 1: faixa HSV de chama ───────────────────────────────────────
    # Vermelho "baixo" (H próximo de 0 e de 179, pois é circular)
    lower_fire1 = np.array([0,   50, 50])
    upper_fire1 = np.array([35, 255, 255])
    mask_hsv1   = cv2.inRange(hsv, lower_fire1, upper_fire1)

    # Vermelho "alto" (H perto de 170–179 = vermelho vivo/âmbar escuro)
    lower_fire2 = np.array([170, 50, 50])
    upper_fire2 = np.array([179, 255, 255])
    mask_hsv2   = cv2.inRange(hsv, lower_fire2, upper_fire2)

    mask_hsv = cv2.bitwise_or(mask_hsv1, mask_hsv2)

    # ── Critério 2: núcleo branco/claro da chama ─────────────────────────────
    # Alta luminosidade + baixa saturação = núcleo quase branco
    lower_core = np.array([0,   0, 200])
    upper_core = np.array([35, 80, 255])
    mask_core  = cv2.inRange(hsv, lower_core, upper_core)

    # ── Critério 3: dominância do canal vermelho (R > G > B) ─────────────────
    b, g, r = cv2.split(blurred)
    # R maior que G e G maior que B (pelo menos por margem)
    mask_rgb = cv2.bitwise_and(
        cv2.compare(r, g, cv2.CMP_GT),   # R > G
        cv2.compare(g, b, cv2.CMP_GT)    # G > B
    )
    # Exige também que R seja suficientemente brilhante (evita pixels escuros)
    _, mask_brightness = cv2.threshold(r, 100, 255, cv2.THRESH_BINARY)
    mask_rgb = cv2.bitwise_and(mask_rgb, mask_brightness)

    # ── Combinação: (HSV OR núcleo) AND dominância RGB ───────────────────────
    mask_color = cv2.bitwise_or(mask_hsv, mask_core)
    mask_final = cv2.bitwise_and(mask_color, mask_rgb)

    # ── Limpeza morfológica ───────────────────────────────────────────────────
    kernel_open  = np.ones((5, 5),  np.uint8)   # remove ruído pequeno
    kernel_close = np.ones((25, 25), np.uint8)  # fecha buracos grandes
    mask_final = cv2.morphologyEx(mask_final, cv2.MORPH_OPEN,  kernel_open)
    mask_final = cv2.morphologyEx(mask_final, cv2.MORPH_CLOSE, kernel_close)

    return mask_final, mask_hsv, mask_rgb

def is_fire_contour(c, area_min, solidity_min):
    """
    Filtra contornos por:
    - Área mínima
    - Solidez (contorno / convex hull) — chamas têm ~0.5–0.9
    - Aspect ratio — chamas tendem a ser mais altas que largas
    """
    area = cv2.contourArea(c)
    if area < area_min:
        return False

    hull_area = cv2.contourArea(cv2.convexHull(c))
    if hull_area == 0:
        return False

    solidity = area / hull_area  # 0.0–1.0
    if solidity < solidity_min / 100.0:
        return False

    # Aspect ratio: chamas não costumam ser perfeitamente quadradas
    _, _, w, h = cv2.boundingRect(c)
    aspect = h / w if w > 0 else 0
    if aspect < 0.3 or aspect > 10:  # descarta extremos
        return False

    return True

while True:
    ok, frame = video.read()

    if not ok:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    area_min    = cv2.getTrackbarPos("Area Min",    "Calibragem")
    solidity_min = cv2.getTrackbarPos("Solidez Min", "Calibragem")

    mask_final, mask_hsv, mask_rgb = build_fire_mask(frame)

    contours, _ = cv2.findContours(
        mask_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    display = frame.copy()
    fire_detected = False

    for c in contours:
        if not is_fire_contour(c, area_min, solidity_min):
            continue

        fire_detected = True
        hull = cv2.convexHull(c)

        # Contorno interno (verde) e hull externo (azul)
        cv2.drawContours(display, [c],    -1, (0, 255, 0),   1)
        cv2.drawContours(display, [hull], -1, (255, 200, 0), 2)

        # Bounding box com label
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        cv2.rectangle(display, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(display, f"FOGO  area={int(area)}",
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)

    # Alerta geral
    if fire_detected:
        cv2.putText(display, "INCENDIO DETECTADO",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 0, 255), 3)

    # Overlay da máscara final sobre o frame (semi-transparente, em laranja)
    overlay = display.copy()
    overlay[mask_final > 0] = (0, 140, 255)
    display = cv2.addWeighted(display, 0.75, overlay, 0.25, 0)

    cv2.imshow("Deteccao de Fogo", display)
    cv2.imshow("Mascara Final",    mask_final)
    cv2.imshow("Mascara HSV",      mask_hsv)
    cv2.imshow("Mascara RGB",      mask_rgb)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()