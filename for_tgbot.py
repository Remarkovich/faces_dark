import os
import cv2
import torch
from ultralytics import YOLO

# Папки
IMAGES_FOLDER = "data"  # Папка с изображениями
OUTPUT_FOLDER = "new_output/"  # Куда сохранять обработанные изображения и txt

# Создаём папку для результатов
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Загружаем YOLOv8 модель (можно использовать face-специализированную)
MODEL_PATH = "best.pt"  # Можно заменить на 'yolov8n-face.pt' для детекции лиц
model = YOLO(MODEL_PATH)

# Проход по всем изображениям в папке
for img_name in os.listdir(IMAGES_FOLDER):
    if img_name.endswith(('.jpg', '.png', '.jpeg')):  # Фильтр изображений
        img_path = os.path.join(IMAGES_FOLDER, img_name)
        img = cv2.imread(img_path)
        height, width, _ = img.shape  # Размер изображения

        # Запускаем YOLOv8
        results = model(img)

        # Открываем файл для записи координат
        txt_filename = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(img_name)[0]}.txt")
        with open(txt_filename, "w") as f:
            for result in results:
                for box in result.boxes:
                    x_min, y_min, x_max, y_max = map(float, box.xyxy[0])  # Координаты (верхний левый и нижний правый угол)
                    conf = box.conf[0].item()  # Доверие модели
                    class_id = int(box.cls[0].item())  # Класс объекта

                    # Преобразуем в формат YOLO (нормализованные значения)
                    x_center = ((x_min + x_max) / 2) / width
                    y_center = ((y_min + y_max) / 2) / height
                    box_width = (x_max - x_min) / width
                    box_height = (y_max - y_min) / height

                    # Записываем в формате YOLO
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

                    # Рисуем боксы на изображении
                    cv2.rectangle(img, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

        # Сохраняем обработанное изображение
        output_img_path = os.path.join(OUTPUT_FOLDER, img_name)
        cv2.imwrite(output_img_path, img)

        print(f"✅ Обработано: {img_name}, сохранено в {txt_filename}")

print("🔥 Готово! Все изображения обработаны.")
