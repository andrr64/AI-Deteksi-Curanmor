from typing import Tuple
import numpy as np
from modules.kalman_filter import create_kalman, kalman_update

class OrangOnline:
    def __init__(self, id_orang, x1y1, x2y2):
        self.id_orang = id_orang
        self.x1y1 = x1y1
        self.x2y2 = x2y2
        self.recognition_count = 0
        self.name = None

        # Inisialisasi Kalman Filter untuk orang ini
        self.kalman_filter = create_kalman()
        self.kalman_filter.x[:4] = np.array((*x1y1, *x2y2)).reshape((4, 1))

    def set_identity(self, name):
        self.name = name
        
    def is_unknown(self) -> bool:
        return self.name is None

    def add_recog_count(self):
        self.recognition_count += 1
    
    def get_label(self):
        name = 'Unknown' if self.is_unknown() else self.name
        return f'People #{self.id_orang} | {name}'
    
    def __str__(self):
        name = 'Unknown' if self.is_unknown() else self.name
        return f'People #{self.id_orang} | {name}'
    
    def get_bbox(self) -> Tuple[int, int, int, int]:
        return (*self.x1y1, *self.x2y2)
    
    def set_coordinates(self, x1y1, x2y2):
        detected_bbox = (*x1y1, *x2y2)
        smoothed_bbox = kalman_update(self.kalman_filter, detected_bbox)

        # Update koordinat dengan hasil smoothing
        x1, y1, x2, y2 = map(int, smoothed_bbox)
        self.x1y1 = (x1, y1)
        self.x2y2 = (x2, y2)
