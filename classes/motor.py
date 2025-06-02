from typing import Tuple
from modules.kalman_filter import create_kalman, kalman_update
import numpy as np
MAX_RECOGNITION = 5

class MotorOnline:
    def __init__(self, id_motor, x1y1, x2y2):
        self.id_motor = id_motor
        self.license_plate: str | None = None
        self.possibility_license_plates: list[str] = []
        self.recognition_count = 0
        self.x1y1 = x1y1
        self.x2y2 = x2y2
        self.previous_bbox = (*x1y1, *x2y2)
        self.max_recognition = MAX_RECOGNITION
        self.baru_datang = True
        self.sedang_dipantau = False
        self.diizinkan = False

        # Inisialisasi Kalman Filter
        self.kalman_filter = create_kalman()
        self.kalman_filter.x[:4] = np.array((*x1y1, *x2y2)).reshape((4, 1))

    def get_bbox(self) -> Tuple[int, int, int, int]:
        return (*self.x1y1, *self.x2y2)
    
    def __str__(self):
        plate = self.license_plate if not self.license_plate_is_none() else 'Unknown'
        return f'Motor #{self.id_motor} | {plate}'
    
    def substract_max_recog(self):
        self.max_recognition -= 2
        if self.max_recognition < 0:
            self.max_recognition = 0
    
    def is_ok_to_recognition(self):
        return self.recognition_count < self.max_recognition
    
    def is_above_max_recog(self):
        return self.recognition_count >= self.max_recognition
    
    def license_plate_is_none(self) -> bool:
        return self.license_plate is None
    
    def reset_recog_count(self):
        self.recognition_count = 0
        
    def set_license_plate(self, plate):
        self.license_plate = plate

    def add_recog_count(self):
        self.recognition_count += 1

    def add_possibility_plate(self, plate):
        self.possibility_license_plates.append(plate)

    def set_coordinates(self, x1y1, x2y2):
        detected_bbox = (*x1y1, *x2y2)
        smoothed_bbox = kalman_update(self.kalman_filter, detected_bbox)
        
        # Simpan previous sebelum update
        self.previous_bbox = (*self.x1y1, *self.x2y2)

        # Update koordinat yang sudah disaring
        x1, y1, x2, y2 = map(int, smoothed_bbox)
        self.x1y1 = (x1, y1)
        self.x2y2 = (x2, y2)
