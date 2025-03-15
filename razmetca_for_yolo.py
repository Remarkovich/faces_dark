import os
import shutil
import random
import re

# Укажите путь к папке с файлами
dataset_path = r"C:\Users\User\Desktop\detect_faces\archive\Chips_Thermal_Face_Dataset"
images_path = os.path.join(dataset_path, "images")  # Папка с изображениями
labels_path = os.path.join(dataset_path, "labels")  # Папка с разметкой

# Пути для разделения
split_paths = {
    "train": {"images": os.path.join(images_path, "train"), "labels": os.path.join(labels_path, "train")},
    "val": {"images": os.path.join(images_path, "val"), "labels": os.path.join(labels_path, "val")},
    "test": {"images": os.path.join(images_path, "test"), "labels": os.path.join(labels_path, "test")},
}

# Создаем папки, если их нет
for split in split_paths.values():
    os.makedirs(split["images"], exist_ok=True)
    os.makedirs(split["labels"], exist_ok=True)

# Функция для извлечения класса из имени файла (перед _)
def get_class(filename):
    match = re.match(r"(\d+)_", filename)
    return match.group(1) if match else None

# Группируем файлы по классам
class_files = {}
image_files = [f for f in os.listdir(images_path) if f.endswith(".jpeg")]

for file in image_files:
    class_id = get_class(file)
    if class_id:
        if class_id not in class_files:
            class_files[class_id] = []
        class_files[class_id].append(file)

# Разбиваем файлы по классам
for class_id, files in class_files.items():
    random.shuffle(files)  # Перемешиваем файлы данного класса

    # Доли для train/val/test
    train_ratio = 0.7
    val_ratio = 0.1
    test_ratio = 0.2

    # Определяем количество файлов
    total_files = len(files)
    train_count = int(total_files * train_ratio)
    val_count = int(total_files * val_ratio)
    test_count = total_files - train_count - val_count  # Остаток в test

    # Разбиваем файлы
    splits = {
        "train": files[:train_count],
        "val": files[train_count:train_count + val_count],
        "test": files[train_count + val_count:]
    }

    # Копируем файлы в соответствующие папки
    for split, split_files in splits.items():
        for file in split_files:
            img_src = os.path.join(images_path, file)
            lbl_src = os.path.join(labels_path, file.replace(".jpg", ".txt"))

            img_dst = os.path.join(split_paths[split]["images"], file)
            lbl_dst = os.path.join(split_paths[split]["labels"], file.replace(".jpg", ".txt"))

            shutil.move(img_src, img_dst)  # Перемещаем изображение
            if os.path.exists(lbl_src):  # Если разметка есть, тоже перемещаем
                shutil.move(lbl_src, lbl_dst)

    print(f"✅ Класс {class_id}: Train: {train_count}, Val: {val_count}, Test: {test_count}")

print("🚀 Разделение завершено!")
