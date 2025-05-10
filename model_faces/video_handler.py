# # video_handler.py

# import cv2
# import os

# def save_video(file, user_id):
#     """Сохраняет видео во временную папку с именем по user_id"""
#     os.makedirs("temp", exist_ok=True)
#     video_path = f"temp/{user_id}.mp4"
#     with open(video_path, "wb") as f:
#         f.write(file)
#     return video_path

# def process_video_to_frames(video_path, username):
#     """Разбивает видео на кадры и сохраняет их в папку dataset/username"""
#     output_dir = f"output_frames/{username}"
#     os.makedirs(output_dir, exist_ok=True)

#     cap = cv2.VideoCapture(video_path)
#     frame_count = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame_path = os.path.join(output_dir, f"{username}_{frame_count:04d}.jpg")
#         cv2.imwrite(frame_path, frame)
#         frame_count += 1

#     cap.release()
#     print(f"[video_handler] Видео разбито на {frame_count} кадров для пользователя {username}.")
#     return frame_count
import os
import cv2
import random
import shutil

def save_video(file, user_id):
    """Сохраняет видео во временную папку с именем по user_id"""
    os.makedirs("temp", exist_ok=True)
    video_path = f"temp/{user_id}.mp4"
    with open(video_path, "wb") as f:
        f.write(file)
    return video_path

def process_video_to_frames(video_path, username, split_ratio=0.8):
    """
    Разбивает видео на кадры, делит на train/val и сохраняет в соответствующие папки.
    """
    temp_dir = f"temp/frames_{username}"
    train_dir = os.path.join("output_frames", "train", username)
    val_dir = os.path.join("output_frames", "val", username)

    # Создаём временную папку для всех кадров
    os.makedirs(temp_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    # 1. Сохраняем все кадры во временную папку
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(temp_dir, f"{username}_{frame_count:04d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_count += 1

    cap.release()

    # 2. Делим кадры на train и val
    all_frames = os.listdir(temp_dir)
    random.shuffle(all_frames)
    split_index = int(len(all_frames) * split_ratio)
    train_frames = all_frames[:split_index]
    val_frames = all_frames[split_index:]

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    # 3. Копируем кадры в соответствующие папки
    for fname in train_frames:
        shutil.copy(os.path.join(temp_dir, fname), os.path.join(train_dir, fname))
    for fname in val_frames:
        shutil.copy(os.path.join(temp_dir, fname), os.path.join(val_dir, fname))

    # 4. Удаляем временную папку с кадрами
    shutil.rmtree(temp_dir)

    print(f"[video_handler] Кадры сохранены в {train_dir} и {val_dir}")
    return frame_count
