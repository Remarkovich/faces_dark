# train_model.py

import os
from ultralytics import YOLO

def train_model(
    dataset_dir: str = r'\output_frames\train',
    model_path: str = 'yolo11x-cls.pt',
    epochs: int = 5,
    imgsz: int = 224,
    batch: int = 4,
    workers: int = 4,
    device: int = 0,
    save_dir: str = 'res_cls'
) -> dict:
    """
    Дообучает YOLO-классификатор на датасете и возвращает метрики валидации.

    Args:
        dataset_dir: путь к папке с разметкой и кадрами (Ultralytics YAML).
        model_path: путь к .pt-файлу предобученной модели.
        epochs: число эпох.
        imgsz: размер входных изображений.
        batch: размер батча.
        workers: количество потоков загрузки данных.
        device: GPU-индекс или 'cpu'.
        save_dir: папка, куда сохранять новые веса и логи.

    Returns:
        Словарь метрик по валидации (как его возвращает `model.val()`).
    """
    if not os.path.isdir(dataset_dir):
        raise FileNotFoundError(f"Dataset not found: {dataset_dir}")

    # Загружаем модель
    model = YOLO(model_path)

    # Обучаем
    model.train(
        data=dataset_dir,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        workers=workers,
        device=device,
        save=True,
        save_period=1,
        plots=True,
        save_dir=save_dir,
    )

    # Валидация
    metrics = model.val()
    return metrics


if __name__ == '__main__':
    # Простой CLI, чтобы можно было запускать вручную:
    import sys
    if len(sys.argv) != 2:
        print("Usage: python train_model.py <dataset_dir>")
        sys.exit(1)

    ds = sys.argv[1]
    print(f"Training on dataset: {ds}")
    m = train_model(ds)
    print("Validation metrics:", m)
