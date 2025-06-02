import cv2
import numpy as np
from insightface.app import FaceAnalysis
from typing import Tuple
from variables import buffalo_l_path

class FaceRecognizer:
    threshold = 0.4
    
    @staticmethod
    def set_threshold(t):
        FaceRecognizer.threshold = t
    
    def __init__(self, model_name="buffalo_l", ctx_id=0):
        self.app = FaceAnalysis(name=model_name, root=buffalo_l_path)
        self.app.prepare(ctx_id=ctx_id)
        self.database = {}
        self.face_length = 0
    def reset_db(self):
        self.database = {}
        self.face_length = 0
        
    def tambah_wajah_ke_database(self, nama, path_gambar):
        img = cv2.imread(path_gambar)
        print(nama, 'OK')
        hasil = self.app.get(img)
        if hasil:
            self.database[nama] = hasil
            self.face_length += 1
        else:
            raise Exception(f'{nama} gagal')
    
    def _normalize(self, v):
        return v / np.linalg.norm(v)

    def identifikasi_wajah(self, frame_crop) -> Tuple[str | None, float | None]:
        if self.face_length ==0:
            return None, None
        wajah = self.app.get(frame_crop)
        if not wajah:
            return None, None
        # Ambil embedding dari hasil upscaling
        embedding = self._normalize(wajah[0].embedding)
        best_match = None
        best_score = -1
                
        for nama, data in self.database.items():
            db_embedding = self._normalize(data[0].embedding)
            score = float(embedding @ db_embedding.T)  # Cosine similarity karena sudah dinormalisasi
            print(f'[FaceRecognizer] Score untuk {nama}: {score:.2f}')
            if score > best_score:
                best_score = score
                best_match = nama

        if best_score >= FaceRecognizer.threshold:  # threshold dapat disesuaikan
            return best_match, best_score
        return None, best_score
