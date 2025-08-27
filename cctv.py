import cv2
import os
import zipfile
from tkinter import Tk, Label
from PIL import Image, ImageTk

class MasImageHelper:
    '''
    이미지 폴더를 관리하며,
    현재 이미지 인덱스를 유지하고,
    다음/이전 이미지 경로를 반환하는 헬퍼 클래스
    '''
    def __init__(self, folder_path):
        self.folder_path = folder_path
        # 지원되는 이미지 확장자만 필터링해 정렬
        self.images = sorted([f for f in os.listdir(folder_path)
                              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.ppm', '.pgm'))])
        self.index = 0
        self.photo = None  # tkinter에서 이미지 유지용 변수

    def get_current_image_path(self):
        if self.images:
            return os.path.join(self.folder_path, self.images[self.index])
        return None

    def next_image(self):
        if self.images:
            self.index = (self.index + 1) % len(self.images)
            return self.get_current_image_path()
        return None

    def prev_image(self):
        if self.images:
            self.index = (self.index - 1) % len(self.images)
            return self.get_current_image_path()
        return None

def extract_zip(zip_path, extract_to):
    '''
    CCTV.zip을 압축 해제하여 extract_to 폴더로 만든다.
    폴더가 이미 있으면 재압축 해제 하지 않음.
    '''
    if not os.path.exists(extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

def main():
    zip_path = 'CCTV.zip'
    extract_folder = 'CCTV'

    # 압축 해제
    extract_zip(zip_path, extract_folder)

    # 이미지 폴더 내 이미지를 관리하는 클래스 초기화
    img_helper = MasImageHelper(extract_folder)

    # Tkinter 윈도우 및 설정
    root = Tk()
    root.title('CCTV Image Viewer')
    root.geometry('800x600')  # 윈도우 크기 지정

    label = Label(root)
    label.pack()

    def show_image(img_path):
        print(f'현재 이미지 표시: {img_path}')  # 디버깅용 출력
        img = Image.open(img_path)
        img_helper.photo = ImageTk.PhotoImage(img)
        label.config(image=img_helper.photo)

    def on_key(event):
        if event.keysym == 'Right':
            img_path = img_helper.next_image()
            if img_path:
                show_image(img_path)
        elif event.keysym == 'Left':
            img_path = img_helper.prev_image()
            if img_path:
                show_image(img_path)

    # 키보드 이벤트 바인딩
    root.bind('<Key>', on_key)

    # 첫 이미지 출력
    first_img = img_helper.get_current_image_path()
    if first_img:
        show_image(first_img)
    else:
        label.config(text='이미지를 찾을 수 없습니다.')

    root.mainloop()

if __name__ == '__main__':
    main()

def detect_people_and_draw_rect(image_path):
    # 이미지 파일 읽기(OpenCV는 BGR 포맷)
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    # HOG 객체 생성 및 기본 사람 탐지기 설정
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    # 사람 탐지
    (regions, _) = hog.detectMultiScale(image, winStride=(8,8), padding=(8,8), scale=1.05)
    
    # 감지된 사람 영역에 빨간색 사각형 그리기 (BGR에서 빨강은 (0, 0, 255))
    for (x, y, w, h) in regions:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0,0,255), 2)
    
    return image
