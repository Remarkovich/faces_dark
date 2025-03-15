import os
import re

# Укажите путь к папке с файлами
folder_path = r"C:\Users\User\Desktop\detect_faces\archive\Chips_Thermal_Face_Dataset\images"

# Проходим по всем файлам в папке
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Удаляем файлы, начинающиеся на "group1"
    if filename.startswith("group1"):
        os.remove(file_path)
        print(f"Удален файл: {filename}")
        continue

print("Обработка завершена.")
