import os

# Укажи путь к папке с .txt файлами разметки
labels_path = r"C:\Users\User\Desktop\detect_faces\archive\Chips_Thermal_Face_Dataset\labels\val"  # Замени на свой путь

# Перебираем все .txt файлы в папке
for file_name in os.listdir(labels_path):
    if file_name.endswith(".txt"):
        file_path = os.path.join(labels_path, file_name)

        # Читаем содержимое файла
        with open(file_path, "r") as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if parts:
                parts[0] = str(int(parts[0]) - 1)  # Вычитаем 1 из индекса класса
                new_lines.append(" ".join(parts))

        # Перезаписываем файл с исправленными индексами
        with open(file_path, "w") as file:
            file.write("\n".join(new_lines))

print("🚀 Все классы в .txt файлах исправлены! Теперь YOLO примет разметку.")
