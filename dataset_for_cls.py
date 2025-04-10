import os
import shutil
import random
from pathlib import Path

SOURCE_DIR = "new_output" 
DEST_DIR = "dataset_split" 
SPLIT_RATIOS = (0.8, 0.1, 0.1)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

splits = ['train', 'val', 'test']
for split in splits:
    for class_dir in os.listdir(SOURCE_DIR):
        dest_path = os.path.join(DEST_DIR, split, class_dir)
        os.makedirs(dest_path, exist_ok=True)

for class_name in os.listdir(SOURCE_DIR):
    class_path = os.path.join(SOURCE_DIR, class_name)
    if not os.path.isdir(class_path):
        continue

    images = [f for f in os.listdir(class_path)
              if f.lower().endswith(IMAGE_EXTENSIONS)]

    random.shuffle(images)
    total = len(images)
    train_end = int(SPLIT_RATIOS[0] * total)
    val_end = train_end + int(SPLIT_RATIOS[1] * total)

    split_files = {
        'train': images[:train_end],
        'val': images[train_end:val_end],
        'test': images[val_end:]
    }

    for split, files in split_files.items():
        for file in files:
            src = os.path.join(class_path, file)
            dst = os.path.join(DEST_DIR, split, class_name, file)
            shutil.copy2(src, dst)

print("Разделение завершено!")
