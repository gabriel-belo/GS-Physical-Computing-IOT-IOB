import cv2
import numpy as np
import matplotlib.pyplot as plt

# Função vazia obrigatória para o createTrackbar
def nothing(x):
    pass

# Captura do vídeo
video = cv2.VideoCapture('queimadas4.mp4')

# Cria a janela de controle
cv2.namedWindow("Calibragem HSV")

# Cria as 6 barras (H, S, V mínimo e máximo)
cv2.createTrackbar("H Min", "Calibragem HSV", 0, 179, nothing)
cv2.createTrackbar("S Min", "Calibragem HSV", 0, 255, nothing)
cv2.createTrackbar("V Min", "Calibragem HSV", 0, 255, nothing)
cv2.createTrackbar("H Max", "Calibragem HSV", 179, 179, nothing)
cv2.createTrackbar("S Max", "Calibragem HSV", 255, 255, nothing)
cv2.createTrackbar("V Max", "Calibragem HSV", 255, 255, nothing)

def drawRectangle(frame, bbox):
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

def displayRectangle(frame, bbox):
    plt.figure(figsize=(20,10))
    frameCopy = frame.copy()
    drawRectangle(frameCopy, bbox)
    frameCopy = cv2.cvtColor(frameCopy, cv2.COLOR_RGB2BGR)
    plt.imshow(frameCopy); plt.axis('off')    

def drawText(frame, txt, location, color = (50,170,50)):
    cv2.putText(frame, txt, location, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

while True:
    ok, frame = video.read()
    
    if not ok:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    #Pré-processamento
    # 1. Blur para reduzir ruído
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    
    # 2. Conversão para HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Pega os valores das barras em tempo real
    h_min = cv2.getTrackbarPos("H Min", "Calibragem HSV")
    s_min = cv2.getTrackbarPos("S Min", "Calibragem HSV")
    v_min = cv2.getTrackbarPos("V Min", "Calibragem HSV")
    h_max = cv2.getTrackbarPos("H Max", "Calibragem HSV")
    s_max = cv2.getTrackbarPos("S Max", "Calibragem HSV")
    v_max = cv2.getTrackbarPos("V Max", "Calibragem HSV")

    # Definir limites da cor do fogo (laranja/amarelo) no espaço HSV
    # lower_fire = np.array([18, 50, 50])
    # upper_fire = np.array([35, 255, 255])
    lower_fire = np.array([h_min, s_min, v_min])
    upper_fire = np.array([h_max, s_max, v_max])

    # 3. Máscara com seus limites (ajustados via Trackbar)
    mask = cv2.inRange(hsv, lower_fire, upper_fire)
    
    # 4. Morfologia para limpar a máscara (Essencial!)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel) # Remove ruído
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # Preenche buracos

    # 5. Find Contours na máscara já limpa
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        if cv2.contourArea(cnt) > 500: # Filtra ruídos pequenos
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "FOGO DETECTADO", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    cv2.imshow('Monitoramento de Queimadas', frame)
    cv2.imshow('Mascara (O que o computador ve)', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

video.release()
cv2.destroyAllWindows()