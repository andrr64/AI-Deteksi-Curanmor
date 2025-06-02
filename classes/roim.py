from classes.motor import MotorOnline
from classes.orang import OrangOnline
from typing import List, Tuple

class ROIMonitor:
    red_line = None
    
    @staticmethod
    def set_red_line(y):
        ROIMonitor.red_line = y
    
    def __init__(self, x1y1, x2y2, data_motor: MotorOnline, list_orang: List[OrangOnline]):
        x1, y1 = x1y1
        x2, y2 = x2y2
        self.roi_bbox: Tuple[int, int, int, int]  = (x1, y1, x2, y2)
        self.data_motor = data_motor
        self.list_orang = list_orang
    
    def is_crossing_redline(self):
        if ROIMonitor.red_line is None:
            raise ValueError("Red line belum diset. Gunakan ROIMonitor.set_red_line(y) terlebih dahulu.")
        x1, y1, x2, y2 = self.roi_bbox
        return max(y1, y2) > ROIMonitor.red_line
