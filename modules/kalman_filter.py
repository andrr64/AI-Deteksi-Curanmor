from filterpy.kalman import KalmanFilter
import numpy as np

def create_kalman():
    kf = KalmanFilter(dim_x=8, dim_z=4)
    kf.F = np.eye(8)  # Transition matrix
    for i in range(4):
        kf.F[i, i+4] = 1  # Add velocity components

    kf.H = np.eye(4, 8)     # Measurement function
    kf.R *= 5.              # Measurement uncertainty
    kf.Q *= 0.1             # Process noise
    kf.P *= 750             # Initial uncertainty
    return kf

def kalman_update(kf, detected_bbox):
    # 1. Prediksi posisi baru
    kf.predict()
    
    # 2. Update berdasarkan deteksi (jika ada)
    kf.update(np.array(detected_bbox).reshape((4, 1)))

    # 3. Ambil hasil posisi yang disaring (smoothed)
    smoothed_bbox = kf.x[:4].reshape(-1).tolist()
    return smoothed_bbox