if __name__ == "__main__":
    from ultralytics import YOLO
    import torch
    torch.cuda.empty_cache()
    model = YOLO("yolov8n.pt")  # Загружаем YOLOv8
    model.train(
        data=r"/home/serv1/CURSACH/detect_faces/archive/Chips_Thermal_Face_Dataset/data.yaml",
        epochs=10,
        imgsz=416,
        batch=4,
        device="cuda",
    )

import torch
print(torch.cuda.is_available())  # Должно вернуть True, если GPU доступен
print(torch.cuda.device_count())  # Количество доступных GPU
print(torch.cuda.get_device_name(0))  # Название первого GPU