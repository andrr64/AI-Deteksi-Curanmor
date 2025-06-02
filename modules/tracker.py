import torch
import numpy as np
from classes.motor import MotorOnline
from classes.orang import OrangOnline
from modules.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from modules.deteksi import YOLOOutput
from typing import List, Tuple, Type
from modules.deteksi import YOLOOutput
from variables import TRACKER_ARGS
from variables import CLASS_MOTORCYCLE, TRACKER_ARGS, CLASS_ROI_MONITORING

class TrackerUniversal:
    def __init__(self, fps: int, wh: Tuple[int, int], obj_class: Type, class_id: int):
        self.tracked_objects: dict[int, object] = {}
        self.tracker = BYTETracker(TRACKER_ARGS, frame_rate=fps)
        self.wh = wh
        self.obj_class = obj_class        # contoh: MotorOnline atau OrangOnline
        self.class_id = class_id          # contoh: CLASS_MOTORCYCLE atau CLASS_PERSON
    
    def reset_tracked(self):
        self.tracked_objects: dict[int, object] = {}
    
    def update(self, detections: List[YOLOOutput]) -> bool:
        if not detections:
            return self.reset_tracked()
        tensors_np = np.array([
            [*det.bbox, det.conf, self.class_id]
            for det in detections
        ], dtype=np.float32)
        tensors = torch.from_numpy(tensors_np)

        stracks = self.tracker.update(tensors, self.wh, self.wh)
        new_tracked = {}
        for obj in stracks:
            x1, y1, x2, y2 = map(int, obj.tlbr)
            obj_id = obj.track_id

            if obj_id in self.tracked_objects:
                old = self.tracked_objects[obj_id]
                old.set_coordinates((x1, y1), (x2, y2))
                new_tracked[obj_id] = old
            else:
                new_tracked[obj_id] = self.obj_class(obj_id, (x1, y1), (x2, y2))

        self.tracked_objects = new_tracked
        return True
