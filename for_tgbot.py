import os
import cv2
import torch
from ultralytics import YOLO

IMAGES_FOLDER = "output_frames_igor"  # Папка с изображениями
OUTPUT_FOLDER = "new_output/igor"  # Куда сохранять обработанные изображения и txt

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
MODEL_PATH = "best.pt"  
model = YOLO(MODEL_PATH)

for img_name in os.listdir(IMAGES_FOLDER):
    if img_name.endswith(('.jpg', '.png', '.jpeg')):  
        img_path = os.path.join(IMAGES_FOLDER, img_name)
        img = cv2.imread(img_path)
        height, width, _ = img.shape 

        results = model(img)

        # Список для хранения координат всех боксов
        all_boxes = []

        txt_filename = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(img_name)[0]}.txt")
        with open(txt_filename, "w") as f:
            for result in results:
                for box in result.boxes:
                    x_min, y_min, x_max, y_max = map(float, box.xyxy[0])  
                    conf = box.conf[0].item() 
                    class_id = 0 

                    # Добавляем все боксы в список
                    all_boxes.append((x_min, y_min, x_max, y_max))

            if all_boxes:
                # Вычисляем среднее значение для всех боксов
                x_min_avg = sum([box[0] for box in all_boxes]) / len(all_boxes)
                y_min_avg = sum([box[1] for box in all_boxes]) / len(all_boxes)
                x_max_avg = sum([box[2] for box in all_boxes]) / len(all_boxes)
                y_max_avg = sum([box[3] for box in all_boxes]) / len(all_boxes)

                # Рассчитываем новые координаты и размер для одного бокса
                x_center = ((x_min_avg + x_max_avg) / 2) / width
                y_center = ((y_min_avg + y_max_avg) / 2) / height
                box_width = (x_max_avg - x_min_avg) / width
                box_height = (y_max_avg - y_min_avg) / height

                # Записываем результат в файл
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

                # Отображаем средний бокс
                cv2.rectangle(img, (int(x_min_avg), int(y_min_avg)), (int(x_max_avg), int(y_max_avg)), (0, 255, 0), 2)

        output_img_path = os.path.join(OUTPUT_FOLDER, img_name)
        cv2.imwrite(output_img_path, img)

        print(f"Обработано: {img_name}, сохранено в {txt_filename}")

print("Все изображения обработаны.")
