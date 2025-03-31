import os
import cv2
import torch
from ultralytics import YOLO

IMAGES_FOLDER = "data"  # Папка с изображениями
OUTPUT_FOLDER = "new_output/"  # Куда сохранять обработанные изображения и txt

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
MODEL_PATH = "best.pt"  
model = YOLO(MODEL_PATH)

for img_name in os.listdir(IMAGES_FOLDER):
    if img_name.endswith(('.jpg', '.png', '.jpeg')):  
        img_path = os.path.join(IMAGES_FOLDER, img_name)
        img = cv2.imread(img_path)
        height, width, _ = img.shape 

        results = model(img)

        txt_filename = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(img_name)[0]}.txt")
        with open(txt_filename, "w") as f:
            for result in results:
                for box in result.boxes:
                    x_min, y_min, x_max, y_max = map(float, box.xyxy[0])  
                    conf = box.conf[0].item() 
                    class_id = int(box.cls[0].item()) 

                    x_center = ((x_min + x_max) / 2) / width
                    y_center = ((y_min + y_max) / 2) / height
                    box_width = (x_max - x_min) / width
                    box_height = (y_max - y_min) / height

                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

                    cv2.rectangle(img, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

        output_img_path = os.path.join(OUTPUT_FOLDER, img_name)
        cv2.imwrite(output_img_path, img)

        print(f" Обработано: {img_name}, сохранено в {txt_filename}")

print("Все изображения обработаны.")
