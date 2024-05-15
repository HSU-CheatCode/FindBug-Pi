import cv2
import torch
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from PIL import Image, ImageDraw, ImageFont
from models.experimental import attempt_load
from utils.general import non_max_suppression
import folder as fd

#AWS Iot 설정


# YOLOv5 모델을 위한 초기화
model = attempt_load('./custom/best.pt')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 이미지 크기
image_width = 640
image_height = 480

# 카메라 연결
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # OpenCV의 BGR 이미지를 RGB로 변환
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 이미지 크기 조정
    img_resized = cv2.resize(img, (image_width, image_height))

    # YOLOv5로 객체 감지
    img_tensor = torch.from_numpy(img_resized).to(device)
    img_tensor = img_tensor.permute(2, 0, 1).float().div(255.0).unsqueeze(0)

    # 추론
    pred = model(img_tensor)[0]
    pred = non_max_suppression(pred, conf_thres=0.7, iou_thres=0.5)[0]

    # 발견된 객체가 있는 경우
    if pred is not None and len(pred) > 0:
        # 이미지를 PIL 이미지로 변환
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # 객체 정보 가져오기
        for det in pred:
            # 객체의 클래스 ID, 신뢰도, 경계 상자 좌표 가져오기
            class_id = int(det[5])
            conf = float(det[4])
            xmin, ymin, xmax, ymax = map(int, det[:4])

            # 클래스명 가져오기
            class_name = model.names[class_id]

            # 이미지에 객체 정보 적기
            draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=2)
            draw.text((xmin, ymin), f"{class_name} ({conf:.2f})", fill="red")

        # 이미지를 파일로 저장
        img_save_path, file_count = fd.folder_path()
        img_save_path = img_save_path+"/detected_bug"+str(file_count)+".jpg"
        pil_img.save(img_save_path)
        print(f"Object detected! Image saved as {img_save_path}")

    # OpenCV 창에 결과 표시
    cv2.imshow('YOLOv5', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료
cap.release()
cv2.destroyAllWindows()
