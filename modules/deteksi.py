import numpy as np
from ultralytics import YOLO
from variables import TENSOR_RT
from typing import List

class YOLOOutput:
    def __init__(self, bbox, cls, conf):
        self.bbox = np.array(bbox, dtype=np.float32)  # konversi bbox ke numpy array
        self.cls = cls
        self.conf = conf
        self.x1, self.y1, self.x2, self.y2 = self.bbox  # unpack langsung dari numpy array

class DeteksiYOLO:
    TIPE_ORANG = 'orang'
    TIPE_KENDARAAN = 'kendaraan'
    TIPE_PLAT = 'plat'
    
    def __init__(self, tipe='orang'):
        if tipe not in (self.TIPE_ORANG, self.TIPE_KENDARAAN, self.TIPE_PLAT):
            raise ValueError(f"Tipe deteksi tidak valid: {tipe}")
        self.tipe = tipe
        self.__model__ = YOLO(TENSOR_RT[tipe], task='detect')
    
    def detect(self, frame, conf_threshold=0.75, classes=[0]) -> List[YOLOOutput]:
        results = self.__model__(frame, conf=conf_threshold, classes=classes, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                xyxy = boxes.xyxy[i].cpu().numpy()  # pastikan dalam numpy array
                conf = float(boxes.conf[i])
                cls = int(boxes.cls[i])
                detections.append(YOLOOutput(xyxy, cls, conf))
        return detections
