import cv2
import os
import glob
import numpy
from pathlib import Path
from PIL import Image
from threading import Condition


from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCameraShutterMode,
    SeekCamera,
    SeekFrame,
)


class Renderer:
    """Contains camera and image data required to render images to the screen."""

    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    """Async callback fired whenever a new frame is available."""
    with renderer.frame_condition:
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    """Async callback fired whenever a camera event occurs."""
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return

        renderer.busy = True
        renderer.camera = camera
        renderer.first_frame = True
        camera.color_palette = SeekCameraColorPalette.SPECTRA
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        if renderer.camera == camera:
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return


def bgra2rgb(bgra):
    row, col, ch = bgra.shape
    assert ch == 4, "ARGB image has 4 channels."
    rgb = numpy.zeros((row, col, 3), dtype="uint8")
    rgb[:, :, 0] = bgra[:, :, 2]
    rgb[:, :, 1] = bgra[:, :, 1]
    rgb[:, :, 2] = bgra[:, :, 0]
    return rgb


def main():
    window_name = "Seek Thermal - Python OpenCV Sample"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    fileName = "igor"
    counter = 100000
    capture = False
    record = False
    ts_first = 0
    ts_last = 0
    frame_count = 0

    output_folder = 'output_frames_igor'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for f in glob.glob(fileName + "*.jpg"):
        os.remove(f)

    print("\nuser controls:")
    print("c:    capture")
    print("r:    record")
    print("q:    quit")

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)

        while True:
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    img = renderer.frame.data

                    if renderer.first_frame:
                        (height, width, _) = img.shape
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False

                    cv2.imshow(window_name, img)

                    if capture or record:
                        rgbimg = bgra2rgb(img)
                        frame_count += 1
                        im = Image.fromarray(rgbimg).convert("RGB")

                        jpg_name = Path(output_folder, f"{fileName}_{counter}.jpg")
                        im.save(jpg_name)
                        counter += 1
                        capture = False

                        if record:
                            ts_last = renderer.frame.header.timestamp_utc_ns
                            if ts_first == 0:
                                ts_first = renderer.frame.header.timestamp_utc_ns

            key = cv2.waitKey(1)
            if key == ord("q"):
                break

            if key == ord("c"):
                capture = True

            if key == ord("r"):
                if not record:
                    record = True
                    renderer.camera.shutter_mode = SeekCameraShutterMode.MANUAL
                    print("\nRecording! Press 'r' to stop recording")
                else:
                    record = False
                    renderer.camera.shutter_mode = SeekCameraShutterMode.AUTO
                    time_s = (ts_last - ts_first) / 1000000000

                    print("\nRecording stopped and video is in myVideo.avi")
                    img_array = []
                    for filename in glob.glob(f"{output_folder}/{fileName}*.jpg"):
                        img = cv2.imread(filename)
                        height, width, layers = img.shape
                        size = (width, height)
                        img_array.append(img)
                    out = cv2.VideoWriter(
                        "myVideo.avi",
                        cv2.VideoWriter_fourcc(*"DIVX"),
                        frame_count / time_s,
                        size,
                    )

                    for i in range(len(img_array)):
                        out.write(img_array[i])
                    out.release()

            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break

    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()
