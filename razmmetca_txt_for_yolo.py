import os
import shutil

# Путь к папке с изображениями и разметками
dataset_path = r"C:\Users\User\Desktop\detect_faces\archive\Chips_Thermal_Face_Dataset"
images_path = os.path.join(dataset_path, "images")  # Папка с картинками
labels_path = os.path.join(dataset_path, "labels")  # Папка с разметками

# Подпапки train, val, test
splits = ["train", "val", "test"]

for split in splits:
    image_folder = os.path.join(images_path, split)  # Где лежат картинки
    label_folder = os.path.join(labels_path, split)  # Куда должны попасть разметки

    os.makedirs(label_folder, exist_ok=True)  # Создаем папку, если её нет
    # print('1')
    # Перебираем все картинки в текущей подпапке
    for file in os.listdir(image_folder):
        # print('2')
        if file.endswith(".jpeg"):
            # print('3')
            txt_file = file.replace(".jpeg", ".txt")  # Имя соответствующего файла разметки
            txt_src = os.path.join(labels_path, txt_file)  # Исходный путь
            txt_dst = os.path.join(label_folder, txt_file)  # Конечный путь

            # Если разметка есть, перемещаем её
            if os.path.exists(txt_src):
                shutil.move(txt_src, txt_dst)
            else:
                print(f"⚠️ Разметка {txt_src} отсутствует!")

print("🚀 Все файлы .txt перемещены в соответствующие папки!")
