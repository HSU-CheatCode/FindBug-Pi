import os
import datetime

def folder_path():
    # 현재 날짜를 가져옵니다.
    today = datetime.datetime.today()
    file_count = 0
    # 날짜를 폴더명 형식으로 변환합니다. (예: "2024-05-09")
    formatted_date = today.strftime("%Y_%m_%d")

    # 이미지 폴더 내에 폴더를 검색하여 없으면 만듭니다.
    today_folder_path = os.path.join("images", formatted_date)
    if not os.path.exists(today_folder_path):
        os.makedirs(today_folder_path)
    else:
        file_count = str(len(os.listdir(today_folder_path)))

    # 생성된 폴더 경로를 반환합니다.
    return today_folder_path, file_count
