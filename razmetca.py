import os
import glob

base_folder = r"C:\Users\User\faces_dark\data\labels"

txt_files = glob.glob(os.path.join(base_folder, "**", "*.txt"), recursive=True)

if not txt_files:
    print("Файлы не найдены")
else:
    for filepath in txt_files:
        print(f"Обрабатываю файл: {filepath}")

        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if lines:
            parts = lines[0].split()  
            if parts and parts[0].isdigit():
                parts[0] = "0" 
                lines[0] = " ".join(parts) + "\n" 

                with open(filepath, "w", encoding="utf-8") as file:
                    file.writelines(lines)
                print("Файл обновлён!\n")
            else:
                print("пропуск\n")

print("Готово!")
