import os
import zipfile
import cv2
from tkinter import Tk, Label
from PIL import Image, ImageTk

class MasImageHelper:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.images = sorted([f for f in os.listdir(folder_path)
                              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.ppm', '.pgm'))])
        self.index = 0
        self.photo = None
        self.opencv_images = []
        self.load_images_with_detection()

    def load_images_with_detection(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        for img_name in self.images:
            img_path = os.path.join(self.folder_path, img_name)
            image = cv2.imread(img_path)
            if image is None:
                self.opencv_images.append(None)
                continue
            regions, _ = self.hog.detectMultiScale(image, winStride=(8,8), padding=(8,8), scale=1.05)
            
            # 보너스 사각형 없이 단순 탐지 여부 출력
            if len(regions) > 0:
                print(f'{img_name}: 사람 탐지됨 ({len(regions)}명)')
            else:
                print(f'{img_name}: 사람 탐지 안 됨')

            self.opencv_images.append(image)

    def get_current_image_path(self):
        if self.images:
            return os.path.join(self.folder_path, self.images[self.index])
        return None

    def get_current_opencv_image(self):
        if self.opencv_images:
            return self.opencv_images[self.index]
        return None

    def next_image(self):
        if self.images:
            self.index += 1
            if self.index >= len(self.images):
                return None
            return self.get_current_image_path()
        return None

def extract_zip(zip_path, extract_to):
    if not os.path.exists(extract_to):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

def opencv_to_photoimage(cv_image, max_size=(800,600)):
    h, w = cv_image.shape[:2]
    scale = min(max_size[0]/w, max_size[1]/h, 1)
    if scale < 1:
        cv_image = cv2.resize(cv_image, (int(w*scale), int(h*scale)))
    cv2_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv2_rgb)
    return ImageTk.PhotoImage(pil_img)

def main():
    zip_path = 'CCTV.zip'
    extract_folder = 'CCTV'
    extract_zip(zip_path, extract_folder)

    img_helper = MasImageHelper(extract_folder)

    root = Tk()
    root.title('CCTV Image Viewer')
    root.geometry('800x600')

    label = Label(root)
    label.pack()

    def show_image():
        opencv_img = img_helper.get_current_opencv_image()
        if opencv_img is None:
            label.config(text='이미지를 읽을 수 없습니다.')
            return
        photo = opencv_to_photoimage(opencv_img)
        img_helper.photo = photo
        label.config(image=photo)

    def on_key(event):
        if event.keysym == 'Return':
            if img_helper.next_image():
                show_image()
            else:
                print('마지막 이미지입니다. 검색을 종료합니다.')
                root.destroy()

    show_image()
    root.bind('<Key>', on_key)
    root.mainloop()

if __name__ == '__main__':
    main()
