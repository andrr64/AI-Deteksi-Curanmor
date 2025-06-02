import cv2
import pygame
import torch
from variables import CLASS_MOTORCYCLE, CLASS_PERSON
from variables import ASSET_PATH_ALARM
from variables import VIDEO_MALAM, VIDEO_SIANG, aerox_malam, aerox_siang, beat_malam, beat_siang
from modules.face_recognizer import FaceRecognizer
from modules.lp_recognizer import LPRecognizer
from modules.geometry import is_inside, intersection, transform_bbox
from paddleocr import PaddleOCR
from modules.cv2_draw import draw_rect, draw_text
from classes.motor import MotorOnline
from classes.roim import ROIMonitor
from classes.orang import OrangOnline
from modules.color import RED, GREEN, YELLOW
from sysdata.kendaraan import authorized_vehicles, vehicle_nicknames
from sysdata.wajah import authorized_faces
from modules.deteksi import DeteksiYOLO, YOLOOutput
from modules.tracker import TrackerUniversal
import time 

VERBOSE = False
MALAM = False
Y_REDLINE = 550

pygame.init()
pygame.mixer.init()
LPRecognizer.init()
torch.set_grad_enabled(False)
FaceRecognizer.set_threshold(0.55 if not MALAM else 0.4)

alarm_sound = pygame.mixer.Sound(ASSET_PATH_ALARM)
alarm_playing = False
face_recognizer = FaceRecognizer(ctx_id=0)
paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')

pendeteksi_kendaraan = DeteksiYOLO(tipe=DeteksiYOLO.TIPE_KENDARAAN)
deteksi_plat = DeteksiYOLO(tipe=DeteksiYOLO.TIPE_PLAT)
pendeteksi_orang = DeteksiYOLO(tipe=DeteksiYOLO.TIPE_ORANG)

frame_count = 0

cap = cv2.VideoCapture(VIDEO_SIANG[2])

if not cap.isOpened():
    exit()
    
fps = int(cap.get(cv2.CAP_PROP_FPS))
max_missing_person_frames = fps * 12  # 12 detik

cache_plat_nomor: dict[int, str] = {}
cache_wajah_orang: dict[int, str] = {}

for name in authorized_faces.keys():
    img_path = authorized_faces[name]
    face_recognizer.tambah_wajah_ke_database(name, img_path)

result_motor = result_orang = result_plat = None

wr = 640
hr = 640
whr = (wr, hr)
frame_count = 0
reset_frame = 60 * fps

ada_maling = False
data_kemalingan = set()

tracker_motor = TrackerUniversal(fps, whr, MotorOnline, CLASS_MOTORCYCLE)
tracker_orang = TrackerUniversal(fps, whr, OrangOnline, CLASS_PERSON)
prev_orang_bbox = None

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Gunakan 'XVID' untuk .avi
out = cv2.VideoWriter('output.mp4', fourcc, fps, whr)

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        print("[INFO] Video selesai")
        break

    original_frame = frame.copy()
    ho, wo = original_frame.shape[:2]
    resized_frame = cv2.resize(original_frame, whr)
    annotated_resized_frame = resized_frame.copy()

    cv2.line(annotated_resized_frame, (0, Y_REDLINE), (wr, Y_REDLINE), RED, thickness=2)
    
    #print(f"\n================ Frame ke-{frame_count} ================\n")
    frame_count += 1
    roi_monitor_terdeteksi: list[ROIMonitor] = []

    if fps % 2 == 0:
        # DETEKSI ORANG 
        prediksi_orang = pendeteksi_orang.detect(resized_frame, classes=[0], conf_threshold=0.7)
        tracker_orang.update(prediksi_orang)
       
        # SISTEM PENGENALAN ORANG
        for id_orang, data_orang in tracker_orang.tracked_objects.items(): # Ganti nama variabel loop
            data_orang: OrangOnline = data_orang
            if id_orang in cache_wajah_orang.keys():
                data_orang.set_identity(name)
                continue
            if data_orang.is_unknown() and frame_count % fps == 0 and data_orang.recognition_count < 10:
                MARGIN_ROI = 0.025
                transformed_bbox = transform_bbox(
                    data_orang.get_bbox(),
                    whr,
                    (wo, ho),
                    MARGIN_ROI
                )
                name, conf = face_recognizer.identifikasi_wajah(
                    frame[
                        transformed_bbox[1]:transformed_bbox[3], 
                        transformed_bbox[0]:transformed_bbox[2]]
                    )
                data_orang.add_recog_count()
                if name is not None and conf is not None:
                    data_orang.set_identity(name)
                    cache_wajah_orang.update({id_orang: name})
    # DETEKSI MOTOR 
    prediksi_motor = pendeteksi_kendaraan.detect(resized_frame, classes=[1], conf_threshold=0.7)
    tracker_motor.update(prediksi_motor)
    
    # SISTEM PENGENALAN MOTOR
    for id_motor, data_motor in tracker_motor.tracked_objects.items():
        data_motor: MotorOnline = data_motor
        x1m, y1m, x2m, y2m = data_motor.get_bbox()
        every_x_f= int(fps/1.5)
        if data_motor.license_plate_is_none() and frame_count % every_x_f == 0 and data_motor.is_ok_to_recognition():
            if id_motor in cache_plat_nomor.keys():
                data_motor.set_license_plate(cache_plat_nomor[id_motor])
            else:
                output_deteksi_plat = deteksi_plat.detect(resized_frame, 0.5, [0])
                ocr_plat_success = False
                if len(output_deteksi_plat) > 0:
                    for plat in output_deteksi_plat:
                        if is_inside(data_motor.get_bbox(), plat.bbox):
                            MARGIN_PLAT = 0.025
                            transformed_bbox = transform_bbox(
                                plat.bbox,
                                whr,
                                (wo, ho),
                                MARGIN_PLAT
                            )
                            roi_plat = original_frame[
                                transformed_bbox[1]:transformed_bbox[3], 
                                transformed_bbox[0]:transformed_bbox[2]]
                            sharpened_roi = LPRecognizer.preprocessing_image(roi_plat)
                            upscaled_roi = LPRecognizer.upscaled_image(roi_plat)
                            ocr_paddle_result = LPRecognizer.ocr(upscaled_roi)
                            plate_text_hasil_ocr = None
                            if ocr_paddle_result and ocr_paddle_result[0] is not None:
                                try:
                                    plate_text_hasil_ocr = ocr_paddle_result[0][0][1][0]
                                    print(f'[LPRecognizer] Motor #{id_motor}: {plate_text_hasil_ocr}')
                                except:
                                    plate_text_hasil_ocr = None
                            if plate_text_hasil_ocr:
                                data_motor.add_possibility_plate(plate_text_hasil_ocr)
                                data_motor.add_recog_count()
                                ocr_plat_success = True
                    if not ocr_plat_success:
                        print(f"[LPRecognizer] Motor ID {id_motor}: Tidak ada plat yang berhasil di-OCR & assign pada percobaan ini.")
                else: 
                    print(f"[LPRecognizer] Motor ID {id_motor}: Tidak ada deteksi plat dari YOLO pada percobaan ini.")

        if data_motor.is_above_max_recog():
            best_match, score = LPRecognizer.try_recognition(authorized_vehicles.keys(), data_motor.possibility_license_plates)
            if best_match is None:
                data_motor.reset_recog_count()
                data_motor.max_recognition -= 2
            else:
                data_motor.set_license_plate(best_match)
                cache_plat_nomor.update({id_motor: best_match})

    # DETEKSI FALSE-POSITIVE MALING
    for data_motor in tracker_motor.tracked_objects.values():
        x1,y1,x2,y2 = data_motor.get_bbox()
        if y1 > Y_REDLINE and y2 < Y_REDLINE:
            pass
        if y1 < Y_REDLINE and y2 < Y_REDLINE:
            if not data_motor.license_plate_is_none() and data_motor.license_plate in data_kemalingan:
                data_kemalingan -= set([data_motor.license_plate])
                print(f'[DEBUG]: DATA KEMALINGAN DIHAPUS {data_motor.license_plate}')
    
    # DETEKSI MALING
    for id_motor, data_motor in tracker_motor.tracked_objects.items():
        x1m, y1m, x2m, y2m = data_motor.get_bbox()
        motor_bbox = data_motor.get_bbox()
        motor_plate = data_motor.license_plate
        ym_max = max(y1m, y2m)
        
        if ym_max > Y_REDLINE and not data_motor.license_plate_is_none():
            list_orang_dekat_motor = []
            for id_orang, data_orang in tracker_orang.tracked_objects.items():
                orang_bbox = data_orang.get_bbox()
                if intersection(motor_bbox, orang_bbox, strictness=0.01):
                    list_orang_dekat_motor.append(data_orang)
                    
            kondisi_1 = any(orang.is_unknown() for orang in list_orang_dekat_motor)
            kondisi_2 = any(not orang.name in authorized_vehicles[motor_plate] for orang in list_orang_dekat_motor)
            
            print('Kondisi orang unknown', kondisi_1)
            print('Kondisi orang tidak di beri askes', kondisi_2)
            aktivitas_maling = kondisi_1 or kondisi_2
            if aktivitas_maling:
                data_kemalingan.add(motor_plate)

    # ============ PENGGAMBARAN KOTAK DAN TEKS ==========================================   
    for data_motor in tracker_motor.tracked_objects.values():
        x1, y1, x2, y2 = map(int, data_motor.get_bbox())  # <-- Cast di sini bro
        label = f' | {vehicle_nicknames[data_motor.license_plate]}' if data_motor.license_plate in vehicle_nicknames else ''
        draw_text(
            annotated_resized_frame,
            f'{str(data_motor)} {label}',
            (x1, y1 - 10),
            color=GREEN
        )
        draw_rect(
            annotated_resized_frame, 
            (x1, y1, x2, y2),
            GREEN
        )
    for data_orang in tracker_orang.tracked_objects.values():
        data_orang: OrangOnline = data_orang
        x1, y1, x2, y2 = map(int, data_orang.get_bbox())  # <-- Cast di sini juga
        draw_text(
            annotated_resized_frame,
            data_orang.get_label(),
            (x1, y1 - 10),
            color=YELLOW
        )
        draw_rect(
            annotated_resized_frame, 
            (x1, y1, x2, y2),
            YELLOW
        )

        if data_kemalingan and not alarm_playing:
            alarm_playing = True
            alarm_sound.play(loops=-1)
            print('KEMALINGAN')
        elif not data_kemalingan and alarm_playing:
            alarm_playing = False
            alarm_sound.stop()
        
        cv2.imshow("Sistem Deteksi Pencurian Motor", annotated_resized_frame)
        out.write(annotated_resized_frame)
        if frame_count == reset_frame:
            frame_count = 0
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
time.sleep(5)
cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()