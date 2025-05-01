import os
import random
import shutil

# Пути к вашим трём папкам
root_folders = [r'output_frames\train\alena', r'output_frames\train\egor', r'output_frames\train\igor']

# Базовая директория, куда будут сохраняться новые папки
base_dir = os.path.dirname('temp_fold')  # или укажите вручную, если нужно

for folder in root_folders:
    folder_name = os.path.basename(folder.rstrip("/\\"))
    images = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    random.shuffle(images)

    split_idx = int(len(images) * 0.8)
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    # Новые папки вне исходной
    train_folder = os.path.join(base_dir, f"train_{folder_name}")
    val_folder = os.path.join(base_dir, f"val_{folder_name}")
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    for img in train_images:
        shutil.copy2(os.path.join(folder, img), os.path.join(train_folder, img))
    for img in val_images:
        shutil.copy2(os.path.join(folder, img), os.path.join(val_folder, img))

print("Разделение завершено.")
