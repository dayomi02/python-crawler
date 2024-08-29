import os
import shutil

def move_file_to_directory(source_path, destination_directory):
    """
    지정된 파일을 대상 디렉터리로 이동합니다.
    
    Parameters:
        source_path (str): 원본 파일 경로
        destination_directory (str): 파일을 이동할 대상 디렉터리 경로
    """
    # 대상 디렉터리가 존재하지 않으면 생성
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # 파일 이름 추출 및 이동할 대상 경로 설정
    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_directory, file_name)

    # 파일 이동
    shutil.move(source_path, destination_path)
    print(f"{file_name} has been moved to {destination_path}")