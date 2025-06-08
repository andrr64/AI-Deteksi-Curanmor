import cv2
import pygame
import torch
import time 
from paddleocr import PaddleOCR
from variables import CLASS_MOTORCYCLE, CLASS_PERSON
from variables import ASSET_PATH_ALARM
from variables import VIDEO_MALAM, VIDEO_SIANG, aerox_malam, aerox_siang, beat_malam, beat_siang
from classes.motor import MotorOnline
from classes.orang import OrangOnline
from sysdata.kendaraan import authorized_vehicles, vehicle_nicknames
from modules.deteksi import DeteksiYOLO, YOLOOutput
from modules.tracker import TrackerUniversal
from modules.color import RED, GREEN, YELLOW
from modules.face_recognizer import FaceRecognizer
from modules.lp_recognizer import LPRecognizer
from modules.cv2_draw import draw_rect, draw_text
from modules.geometry import is_inside, intersection, transform_bbox, merge_bbox
from modules.sistem_deteksi_curanmor import SistemAntiCuranmor
from data_pengujian import sample_1, sample_2
import os
from datetime import datetime as dt, timedelta
from collections import deque

VERBOSE = False
Y_REDLINE = 550
Y_REDLINE_720 = int(Y_REDLINE * 720 / 640)

pygame.init()
pygame.mixer.init()
LPRecognizer.init()
torch.set_grad_enabled(False)

alarm_sound = pygame.mixer.Sound(ASSET_PATH_ALARM)
alarm_playing = False
face_recognizer = FaceRecognizer(ctx_id=0)

pendeteksi_kendaraan = DeteksiYOLO(tipe=DeteksiYOLO.TIPE_KENDARAAN)
pendeteksi_plat = DeteksiYOLO(tipe=DeteksiYOLO.TIPE_PLAT)
pendeteksi_orang = DeteksiYOLO(tipe=DeteksiYOLO.TIPE_ORANG)

wr = 640
hr = 640
wd = 1280
hd = 720
whr = (wr, hr)
whd = (wd, hd)
MAX_HISTORY_SECONDS = 5 # Durasi riwayat orang di sekitar motor yang diambil

with open('results.txt', 'w+t') as file:
    pass

def run(path, kondisi_malam, dict_wajah: dict[str, str], dict_kendaraan: dict[str, list[str]]):
    rel_path = os.path.relpath(path, 'videos')  # Contoh: 'siang/VID_2025....mp4'
    output_path = os.path.join('output', rel_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)    
    
    face_recognizer.reset_db()
    for name, face_path in dict_wajah.items():
        face_recognizer.tambah_wajah_ke_database(name, face_path)

    cap = cv2.VideoCapture(path)
    frame_count = 0

    FaceRecognizer.set_threshold(0.55 if not kondisi_malam else 0.4)

    if not cap.isOpened():
        exit()
  
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    alarm_playing = False
    alarm_sound.stop()
    sistem_manajemen_motor = SistemAntiCuranmor(
        data_sistem=dict_kendaraan,
        debug=True
    )

    cache_plat_nomor: dict[int, str] = {}
    cache_data_motor: dict[int, OrangOnline] = {}
    cache_wajah_orang: dict[int, str] = {}
    cache_orang_dilingkungan_motor: deque[list[str | None]] = deque(maxlen=10)
    
    frame_count = 0
    reset_frame = 60 * fps

    tracker_motor = TrackerUniversal(fps, whr, MotorOnline, CLASS_MOTORCYCLE)
    tracker_orang = TrackerUniversal(fps, whr, OrangOnline, CLASS_PERSON)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    out = cv2.VideoWriter(output_path, fourcc, fps, whd)

    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            print("[INFO] Video selesai")
            break

        original_frame = frame.copy()
        ho, wo = original_frame.shape[:2]
        resized_frame = cv2.resize(original_frame, whr)
        annotated_resized_frame = resized_frame.copy()
        annotated_frame = cv2.resize(original_frame, (1280, 720))
        
        cv2.line(annotated_frame, (0, Y_REDLINE_720), (1280, Y_REDLINE_720), RED, thickness=2)
        
        #print(f"\n================ Frame ke-{frame_count} ================\n")
        frame_count += 1

        if frame_count % 2 == 0:
            # DETEKSI ORANG 
            prediksi_orang = pendeteksi_orang.detect(resized_frame, classes=[0], conf_threshold=0.7)
            tracker_orang.update(prediksi_orang)
            print(f'[DeteksiOrang]: {len(prediksi_orang)}')
            # SISTEM PENGENALAN ORANG
            for id_orang, data_orang in tracker_orang.tracked_objects.items(): # Ganti nama variabel loop
                data_orang: OrangOnline = data_orang
                if id_orang in cache_wajah_orang.keys():
                    data_orang.set_identity(name)
                    continue
                if data_orang.is_unknown() and frame_count % fps == 0 and data_orang.recognition_count < 30:
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
                    if name is not None and conf is not None:
                        data_orang.set_identity(name)
                        cache_wajah_orang.update({id_orang: name})
                        data_orang.add_recog_count()
                    else:
                        print(f'[FaceRecognizer] tidak ditemukan wajah pada orang #{data_orang.id_orang}')
        if frame_count % 1 == 0:
            # DETEKSI MOTOR 
            prediksi_motor = pendeteksi_kendaraan.detect(resized_frame, classes=[1], conf_threshold=0.65)
            print(f'[DeteksiMotor] terdeteksi {len(prediksi_motor)} motor')
            tracker_motor.update(prediksi_motor)
            
            
            # SISTEM PENGENALAN MOTOR
            for id_motor, data_motor in tracker_motor.tracked_objects.items():
                data_motor: MotorOnline = data_motor
                if id_motor in cache_data_motor.keys():
                    tracker_motor.tracked_objects[id_motor] = cache_data_motor[id_motor]
                else:
                    cache_data_motor[id_motor] = data_motor
                every_x_f= int(fps/2)
                if data_motor.license_plate_is_none() and frame_count % every_x_f == 0:
                    output_deteksi_plat = pendeteksi_plat.detect(resized_frame, 0.4, [0])
                    ocr_plat_success = False
                    if len(output_deteksi_plat) > 0:
                        for plat in output_deteksi_plat:
                            draw_rect(
                                annotated_frame,
                                transform_bbox(plat.bbox, whr, whd),
                                YELLOW
                            )
                            if is_inside(data_motor.get_bbox(), plat.bbox):
                                MARGIN_PLAT = 0.025
                                transformed_bbox = transform_bbox(
                                    plat.bbox,
                                    whr,
                                    (wo, ho),
                                    MARGIN_PLAT
                                )
                                
                                sharpened_roi = LPRecognizer.preprocessing_image(
                                    original_frame[
                                        transformed_bbox[1]:transformed_bbox[3], 
                                        transformed_bbox[0]:transformed_bbox[2]]
                                )
                                upscaled_roi = LPRecognizer.upscaled_image(sharpened_roi)
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
                    data_motor.reset_recog_count()
                    data_motor.max_recognition -= 1
                    best_match, score = LPRecognizer.try_recognition(authorized_vehicles.keys(), data_motor.possibility_license_plates)
                    if not (best_match is None):
                        data_motor.set_license_plate(best_match)
                        cache_plat_nomor.update({id_motor: best_match})
                        print(f'[PLAT OK ] {best_match}')
                    else:
                        print('[ERROR] PLAT TIDAK BISA DIKENALI')

        active_lp = {x.license_plate for x in tracker_motor.tracked_objects.values() if not x.license_plate_is_none()}
        list_nama_di_lingkungan: list[str | None] = [x.name for x in tracker_orang.tracked_objects.values()]     
        if frame_count % fps == 0:
            cache_orang_dilingkungan_motor.append(list_nama_di_lingkungan)
            print(f"Cache orang diperbarui. Ukuran cache: {len(cache_orang_dilingkungan_motor)}.")
        
        for plat_in_system in sistem_manajemen_motor.data_status_kendaraan.keys():
            sistem_manajemen_motor.set_status_didalam_frame(plat_in_system, plat_in_system in active_lp)

        # --- 2. PENGUJIAN SKENARIO 1: PELINTASAN BATAS MENCURIGAKAN ---
        for id_motor, data_motor in tracker_motor.tracked_objects.items():
            if not data_motor.license_plate_is_none():
                motor_plate = data_motor.license_plate
                if sistem_manajemen_motor.data_status_kendaraan[motor_plate].status_maling:
                    continue
                sistem_manajemen_motor.update_terakhir_dilihat(motor_plate)
                data_status_motor = sistem_manajemen_motor.data_status_kendaraan[motor_plate]
                x1, y1, x2, y2 = data_motor.get_bbox()
                ymax =  max(y1, y2)
                My = ymax > Y_REDLINE 
                if My: 
                    nama_terotorisasi = dict_kendaraan.get(motor_plate, []) # Ambil nama terotorisasi
                    Op = not any(p_name in nama_terotorisasi for p_name in list_nama_di_lingkungan if p_name is not None)
                    Oe = not any(p_name for p_name in list_nama_di_lingkungan if p_name is not None)
                    Ou = any(p_name for p_name in list_nama_di_lingkungan if p_name is not None and p_name not in nama_terotorisasi)
                    
                    print(Op, Oe, Ou)
                    if Op and (Oe or Ou):
                        data_status_motor.status_maling = True
                        print(f"!!! ALARM !!! Motor {motor_plate} terdeteksi MALING (Skenario 1: Melintasi batas mencurigakan)!")

        # --- 3. PENGUJIAN SKENARIO 2: PELINTASAN BATAS MENCURIGAKAN ---
        recent_5_seconds_cache = list(cache_orang_dilingkungan_motor)[-MAX_HISTORY_SECONDS:]
        set_orang_5detik_terakhir: set[str | None] = set()
        
        for detection_list_per_second in recent_5_seconds_cache:
            for p_name in detection_list_per_second:
                set_orang_5detik_terakhir.add(p_name)
                
        for plat, data_status in sistem_manajemen_motor.data_status_kendaraan.items():
            if data_status.status_maling:
                continue
            Ka = (plat not in active_lp) and data_status.status_didalam_frame 
            if Ka: # Jika Ka = True (motor hilang dari pandangan)
                now = dt.now()
                elapsed = now - data_status.terakhir_dilihat # Waktu sejak terakhir terlihat
                Kt = elapsed > timedelta(seconds=2) # Kt: Tidak terdeteksi > 2 detik

                if Kt: # Jika Kt = True (sudah 2 detik lebih hilang)
                    nama_terotorisasi = dict_kendaraan.get(plat, []) # Ambil nama terotorisasi
                    Ie = any(p_name is None or (p_name is not None and p_name not in nama_terotorisasi)
                            for p_name in set_orang_5detik_terakhir)
                    Np = all(len(d_list) == 0 for d_list in recent_5_seconds_cache)
                    # Logika Skenario 2: (Ka AND Kt AND (Ie OR Np))
                    if Ie or Np: 
                        data_status.status_maling = True
                        print(f"!!! ALARM !!! Motor {plat} terdeteksi MALING (Skenario 2: Hilang mencurigakan)!")
                    else:
                        data_status.status_didalam_frame = False # Anggap hilang dengan aman
                else:
                    #    Jika Kt false, motor belum cukup lama hilang untuk memicu skenario 2 ini.
                    pass
            else:
            #    Jika Ka false, motor tidak dianggap hilang dari pandangan.
                pass
        
        # --- 4 SISTEM DEAKTIVASI ALARM MALING MOTOR
        # SKENARIO: MOTOR KEMBALI KE DALAM AREA PANTAU (NILAI YMAX DIBAHWA YREDLINE)
        maling_lp = [
            plat for plat, data in sistem_manajemen_motor.data_status_kendaraan.items()
            if data.status_maling == True]
        for data_motor in tracker_motor.tracked_objects.values():
            if not data_motor.license_plate_is_none():
                plat = data_motor.license_plate
                if plat in maling_lp:
                    x1,y1,x2,y2 = data_motor.get_bbox()
                    nama_terotorisasi = dict_kendaraan.get(plat, []) # Ambil nama terotorisasi
                    ymax  = max(y1, y2)
                    Pe = any(x in nama_terotorisasi for x in set_orang_5detik_terakhir)
                    if ymax <  Y_REDLINE or Pe:
                        sistem_manajemen_motor.data_status_kendaraan[plat].status_maling = False
                        sistem_manajemen_motor.data_status_kendaraan[plat].status_didalam_frame = True
                
        # ============ PENGGAMBARAN KOTAK (RECTANGLE) DULU ==========================================
        for data_motor in tracker_motor.tracked_objects.values():
            x1, y1, x2, y2 = transform_bbox(
                data_motor.get_bbox(),
                whr,
                (1280, 720)
            )
            draw_rect(
                annotated_frame,
                (x1, y1, x2, y2),
                GREEN
            )

        for data_orang in tracker_orang.tracked_objects.values():
            data_orang: OrangOnline = data_orang
            x1, y1, x2, y2 = transform_bbox(
                data_orang.get_bbox(),
                whr,
                (1280, 720)
            )
            draw_rect(
                annotated_frame,
                (x1, y1, x2, y2),
                YELLOW
            )

        # ============ LALU GAMBAR TEKS-NYA =========================================================
        for data_motor in tracker_motor.tracked_objects.values():
            x1, y1, _, _ = transform_bbox(
                data_motor.get_bbox(),
                whr,
                (1280, 720)
            )
            label = f' | {vehicle_nicknames[data_motor.license_plate]}' if data_motor.license_plate in vehicle_nicknames else ''
            draw_text(
                annotated_frame,
                f'{str(data_motor)} {label}',
                (x1, y1 - 10),
                color=GREEN
            )

        for data_orang in tracker_orang.tracked_objects.values():
            data_orang: OrangOnline = data_orang
            x1, y1, _, _ = transform_bbox(
                data_orang.get_bbox(),
                whr,
                (1280, 720)
            )
            draw_text(
                annotated_frame,
                data_orang.get_label(),
                (x1, y1 - 10),
                color=YELLOW
            )

        
        frame_h, frame_w = annotated_frame.shape[:2]
        margin = 10  # jarak dari tepi layar
        line_height = 20  # tinggi per baris teks
        baris_ke = 0

        # Tampilkan status kendaraan dari bawah ke atas
        for plate, data_kendaraan in reversed(list(sistem_manajemen_motor.data_status_kendaraan.items())):
            status_text = str(data_kendaraan)
            pos_y = frame_h - margin - (baris_ke * line_height)
            draw_text(
                annotated_frame,
                status_text,
                (margin, pos_y),
                color=YELLOW  # atau warna lain kalau mau
            )
            baris_ke += 1

        if sistem_manajemen_motor.is_ada_maling and alarm_playing:
            alarm_playing = True
            alarm_sound.play(loops=-1)
        elif not sistem_manajemen_motor.is_ada_maling and alarm_playing:
            alarm_playing = False
            alarm_sound.stop()
        
        out.write(annotated_frame)
        cv2.imshow('Deteksi', annotated_frame)

        if frame_count == reset_frame:
            frame_count = 0
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
            
    time.sleep(3)
    result = f'[PENELITIAN] SELESAI : {path} | Ada Maling -> {sistem_manajemen_motor.is_ada_maling}'
    with open('results.txt', '+a') as file:
        file.writelines(result + '\n')
    
    print(result)
    cap.release()
    cv2.destroyAllWindows()

from data_pengujian import sample_1_aerox, sample_2_aerox, sample_3_beat

# for data in sample_1_aerox:
#     run(data['path'], data['malam'], data['dict_wajah'], data['dict_kendaraan'])
    
# for data in sample_2_aerox:
#     run(data['path'], data['malam'], data['dict_wajah'], data['dict_kendaraan'])

for data in sample_3_beat:
    run(data['path'], data['malam'], data['dict_wajah'], data['dict_kendaraan'])

# # data = sample_3_beat[3]
# data = sample_3_beat[7]
# run(data['path'], data['malam'], data['dict_wajah'], data['dict_kendaraan'])
    
pygame.mixer.quit()