import requests
import serial

# Serial number 생성 및 URL 설정
serial_num = serial.write_serial_file().strip()
print(serial_num)
url = 'http://findbugs.kro.kr/upload/' + str(serial_num)
print(url)

# 파일 경로 설정
file_path = 'image2.jpg'

# 파일 열기 및 요청 전송
with open(file_path, 'rb') as image_file:
    files = {'file': (file_path, image_file, 'image/jpg')}
    response = requests.post(url, files=files)

# 응답 처리
if response.status_code == 200:
    try:
        print('이미지 업로드 성공:', response.json())
    except requests.exceptions.JSONDecodeError:
        print('이미지 업로드 성공:', response.text)
else:
    print('이미지 업로드 실패:', response.status_code, response.text)
