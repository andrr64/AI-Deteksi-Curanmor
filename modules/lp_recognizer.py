from ultralytics import YOLO
from paddleocr import PaddleOCR
from difflib import SequenceMatcher
from paddleocr import PaddleOCR
import re
from modules.img_preprocessing import sharp_img
from modules.upscale import API_upscale_frame

class LPRecognizer:
    paddle_ocr = None
    
    @staticmethod
    def init():
        LPRecognizer.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    
    @staticmethod
    def extract_digits(text):
        return ''.join(re.findall(r'\d+', text))
    
    @staticmethod
    def ocr(frame, cls= True) -> str | None:
        try:
            return LPRecognizer.paddle_ocr.ocr(frame, cls=cls)
        except Exception as e_ocr_paddle:
            print(f"[ERROR] PaddleOCR exception : {e_ocr_paddle}")
            return None

    @staticmethod
    def preprocessing_image(frame):
        sharpened = sharp_img(frame)
        return sharpened
    
    @staticmethod
    def upscaled_image(frame):
        try:
            temp_upscaled = API_upscale_frame(frame)
            return temp_upscaled
        except Exception as e:
            return frame           

    @staticmethod
    def try_recognition(list_plate, list_ocr_result):
        if not list_plate or not list_ocr_result:
            return None, 0.0

        best_match = None
        best_score = 0.0

        for plate in list_plate:
            plate_digits = LPRecognizer.extract_digits(plate)
            if not plate_digits:
                continue

            for ocr_result in list_ocr_result:
                ocr_digits = LPRecognizer.extract_digits(ocr_result)
                if not ocr_digits:
                    continue
                similarity = SequenceMatcher(None, plate_digits, ocr_digits).ratio()
                if similarity > best_score:
                    best_score = similarity
                    best_match = plate 

        return best_match, best_score