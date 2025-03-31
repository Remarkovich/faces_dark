if __name__ == "__main__":
    from ultralytics import YOLO
    import torch
    torch.cuda.empty_cache()
    model = YOLO("yolov8n.pt") 
    model.train(
        data=r"C:\Users\User\faces_dark\data\data.yaml",
        epochs=5,
        imgsz=312,
        batch=4,
        device="cuda",
    )
