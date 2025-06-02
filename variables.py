from argparse import Namespace

buffalo_l_path = 'models/buffalo_l'

def model_path_tensorrt(filename: str):
    return f'models/TensorRT/{filename}'

TENSOR_RT = {
    'orang': model_path_tensorrt('deteksi-orang-v2.engine'),
    'kendaraan': model_path_tensorrt('deteksi-kendaraan-v2.engine'),
    'plat': model_path_tensorrt('deteksi-plat-v2.engine')
}

CLASS_MOTORCYCLE = 0xa1
CLASS_PERSON = 0xa2
CLASS_LICENSE_PLATE = 0xa3
CLASS_ROI_MONITORING = 0xa4

ASSET_PATH_ALARM = "assets/alarm.wav"

TRACKER_ARGS = Namespace(
    track_thresh=0.5,
    match_thresh=0.8,
    track_buffer=30,
    min_box_area=10,
    mot20=False
)

VIDEO_MALAM = [
    'videos/malam/VID_20250522_140554652_1.mp4',
    'videos/malam/VID_20250522_140554652_2.mp4',
    'videos/malam/video_malam1.mp4',
]

VIDEO_SIANG = [
    'videos/siang/VID_20250522_140554652_1.mp4',
    'videos/siang/VID_20250522_140554652_2.mp4',
    'videos/siang/VID_20250522_140554652_3.mp4',
]

aerox_malam = [
    {'pemilik': 'Andreas', 'maling': 'Shafiq', 'path': 'videos/aerox-malam/VID_20250529_180932155~2-andre-shafiq.mp4'},
    {'pemilik': 'Andreas', 'maling': 'Randi', 'path': 'videos/aerox-malam/VID_20250529_181408115~2-andre-randi.mp4'},
    {'pemilik': 'Fajar', 'maling': 'Shafiq', 'path': 'videos/aerox-malam/VID_20250529_181543377~2-fajar-shafiq.mp4'},
    {'pemilik': 'Shafiq', 'maling': 'Andreas', 'path': 'videos/aerox-malam/VID_20250529_181737364~2-shafiq-andreas.mp4'}
]

aerox_siang = [
    {'pemilik': 'Andreas', 'maling': 'Randi', 'path': 'videos/aerox-siang/VID_20250529_165149928~2-andreas-randi.mp4'},
    {'pemilik': 'Shafiq', 'maling': 'Andreas', 'path': 'videos/aerox-siang/VID_20250529_165434804~2-shafiq-andreas.mp4'},
    {'pemilik': 'Fajar', 'maling': 'Shafiq', 'path': 'videos/aerox-siang/VID_20250529_165655053~2-fajar-shafiq.mp4'}
]

beat_malam = [
    {'pemilik': 'Andreas', 'maling': 'Randi', 'path': 'videos/beat-malam/VID_20250529_182126862-andreas-randi.mp4'},
    {'pemilik': 'Shafiq', 'maling': 'Fajar', 'path': 'videos/beat-malam/VID_20250529_182526100-shafiq-fajar.mp4'},
    {'pemilik': 'Fajar', 'maling': 'Shafiq', 'path': 'videos/beat-malam/VID_20250529_182631408-fajar-shafiq.mp4'},
    {'pemilik': 'Randi', 'maling': 'Andreas', 'path': 'videos/beat-malam/VID_20250529_182759428-randi-andreas.mp4'}
]

beat_siang = [
    {'pemilik': 'Shafiq', 'maling': 'Randi', 'path': 'videos/beat-siang/VID_20250529_170128184~2-shafiq-randi.mp4'},
    {'pemilik': 'Andreas', 'maling': 'Fajar', 'path': 'videos/beat-siang/VID_20250529_170249316~2-andreas-fajar.mp4'},
    {'pemilik': 'Fajar', 'maling': 'Shafiq', 'path': 'videos/beat-siang/VID_20250529_170434119~2-fajar-shafiq.mp4'},
    {'pemilik': 'Randi', 'maling': 'Andreas', 'path': 'videos/beat-siang/VID_20250529_170434119~3-randi-andreas.mp4'}
]
