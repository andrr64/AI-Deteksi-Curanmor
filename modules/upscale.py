import cv2
import requests
import numpy as np

def API_upscale_frame(frame: np.ndarray) -> np.ndarray:
    success, encoded_img = cv2.imencode('.jpg', frame)
    if not success:
        raise ValueError("❌ Gagal encode frame")

    files = {'file': ('frame.jpg', encoded_img.tobytes(), 'image/jpeg')}
    response = requests.post("http://localhost:8000/sr", files=files)

    if response.status_code != 200:
        print("❌ Error dari server:", response.text)
        raise RuntimeError(f"Upscale gagal: {response.status_code}")

    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    upscaled_frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if upscaled_frame is None:
        raise ValueError("❌ Gagal decode response dari server ke gambar")

    return upscaled_frame
