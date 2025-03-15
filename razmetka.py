import os
import re

# Укажите путь к папке с файлами
folder_path = r"C:\Users\User\Desktop\detect_faces\archive\Chips_Thermal_Face_Dataset\annotations_yolo_format"

# Проходим по всем файлам в папке
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Удаляем файлы, начинающиеся на "group1"
    if filename.startswith("group1"):
        os.remove(file_path)
        print(f"Удален файл: {filename}")
        continue

    # Обрабатываем только файлы .txt
    if filename.endswith(".txt"):
        match = re.match(r"(\d+)_", filename)  # Извлекаем первую цифру перед _
        if match:
            first_digit = match.group(1)  # Получаем цифру
            
            # Читаем содержимое файла
            with open(file_path, "r") as file:
                content = file.read()
            
            # Заменяем первый 0 на нужную цифру
            updated_content = re.sub(r"^0", first_digit, content, count=1)
            
            # Записываем изменения обратно в файл
            with open(file_path, "w") as file:
                file.write(updated_content)
            
            print(f"Обновлен файл: {filename}")

print("Обработка завершена.")
