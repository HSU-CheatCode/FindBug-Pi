import os
import cv2
import numpy as np
import time
import serial
import requests
import filename

saved_time = 0

# 파일 경로 설정
weight_path = "./weights/yolo-fastest-1_last.weights"
cfg_path = "./module/yolo-fastest-1.1.cfg"
names_path = "./yolo_names.txt"

# 파일 존재 여부 확인
if not os.path.exists(weight_path):
    print(f"Weights file not found: {weight_path}")
if not os.path.exists(cfg_path):
    print(f"CFG file not found: {cfg_path}")
if not os.path.exists(names_path):
    print(f"Names file not found: {names_path}")

# YOLO 가중치 파일과 CFG 파일 로드
YOLO_net = cv2.dnn.readNet(weight_path, cfg_path)

# YOLO NETWORK 재구성
classes = []
with open(names_path, "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = YOLO_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in YOLO_net.getUnconnectedOutLayers()]

# Serial number 생성 및 URL 설정
serial_num = serial.write_serial_file().strip()
url = 'http://findbugs.kro.kr/upload'

# 웹캠 신호 받기
cap = cv2.VideoCapture(0)

# 이미지를 저장할 디렉터리 생성
output_dir = "images"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

while True:
    # 웹캠 프레임
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    h, w, c = frame.shape

    # YOLO 입력
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    YOLO_net.setInput(blob)
    outs = YOLO_net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                dw = int(detection[2] * w)
                dh = int(detection[3] * h)
                # Rectangle coordinate
                x = int(center_x - dw / 2)
                y = int(center_y - dh / 2)
                boxes.append([x, y, dw, dh])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.7, nms_threshold=0.5, top_k=2)
    
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            score = confidences[i]

            # 경계상자와 클래스 정보 이미지에 입력
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, f"{label} {score:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # 30초 지나면 작동
        now = time.time()
        if now - saved_time > 30:
            saved_time = now

            file_name, send_time = filename.make_file_name(serial_num)

            params = {
                'imei':serial_num,
                'bugName':'cockroach',
                'detectedTime':send_time
            }

            # 객체가 탐지된 이미지를 저장
            image_path = os.path.join(output_dir, f"{file_name}.jpg")
            cv2.imwrite(image_path, frame)

            with open(image_path, 'rb') as image_file:
                # 감지한 객체를 서버에 전송
                files = {'file':(f"{file_name}.jpg", image_file, 'image/jpeg')}
                response = requests.post(url, files=files, params=params)

            if response.status_code == 200:
                try:
                    print('이미지 업로드 성공:', response.json())
                except requests.exceptions.JSONDecodeError:
                    print('이미지 업로드 성공:', response.text)
            else:
                print('이미지 업로드 실패:', response.status_code, response.text)

    # 이미지 표시
    cv2.imshow("YOLO Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
