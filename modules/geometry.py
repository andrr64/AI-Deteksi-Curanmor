from typing import Tuple

def is_inside(bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> bool:
    """
    Periksa apakah bbox2 sepenuhnya berada di dalam bbox1.

    Args:
        bbox1 (Tuple[int, int, int, int]): Bounding box referensi dalam format (x1, y1, x2, y2).
        bbox2 (Tuple[int, int, int, int]): Bounding box target yang ingin diperiksa.

    Returns:
        bool: True jika bbox2 sepenuhnya berada di dalam bbox1, False jika tidak.
    """
    x1_a, y1_a, x2_a, y2_a = bbox1
    x1_b, y1_b, x2_b, y2_b = bbox2

    return (x1_b >= x1_a and y1_b >= y1_a and
            x2_b <= x2_a and y2_b <= y2_a)


def transform_bbox(
    xyxyS: Tuple[int, int, int, int],
    whS: Tuple[int, int],
    whT: Tuple[int, int],
    margin: float = 0
) -> Tuple[int, int, int, int]:
    """
    Transformasikan bounding box dari dimensi sumber ke dimensi target, dengan opsi penambahan margin.

    Args:
        xyxyS (Tuple[int, int, int, int]): Koordinat bounding box pada dimensi sumber (x1, y1, x2, y2).
        whS (Tuple[int, int]): Ukuran (width, height) dari dimensi sumber.
        whT (Tuple[int, int]): Ukuran (width, height) dari dimensi target.
        margin (float, optional): Margin tambahan relatif terhadap ukuran bounding box (0 berarti tidak ada tambahan).

    Returns:
        Tuple[int, int, int, int]: Bounding box hasil transformasi ke ukuran target.
    """
    scale_x = whT[0] / whS[0]
    scale_y = whT[1] / whS[1]
    
    x1s, y1s, x2s, y2s = xyxyS
    roi_w_t = (x2s - x1s) * scale_x
    roi_h_t = (y2s - y1s) * scale_y
    wT, hT = whT
    
    x1_t = int((x1s * scale_x) - (margin * roi_w_t))
    y1_t = int((y1s * scale_y) - (margin * roi_h_t))
    x2_t = int((x2s * scale_x) + (margin * roi_w_t))
    y2_t = int((y2s * scale_y) + (margin * roi_h_t))
    
    # Batasi agar tetap dalam dimensi target
    x1_t = max(0, min(x1_t, wT - 1))
    y1_t = max(0, min(y1_t, hT - 1))
    x2_t = max(0, min(x2_t, wT - 1))
    y2_t = max(0, min(y2_t, hT - 1))
    
    return (x1_t, y1_t, x2_t, y2_t)


def intersection(
    bbox1: Tuple[int, int, int, int],
    bbox2: Tuple[int, int, int, int],
    strictness: float = 0.0
) -> bool:
    """
    Periksa apakah dua bounding box saling berpotongan berdasarkan tingkat strictness (berdasarkan IoU).

    Args:
        bbox1 (Tuple[int, int, int, int]): Bounding box pertama (x1, y1, x2, y2).
        bbox2 (Tuple[int, int, int, int]): Bounding box kedua (x1, y1, x2, y2).
        strictness (float, optional): Nilai antara 0.0 - 1.0 untuk menentukan seberapa ketat batas interseksi.
            - 0.0: asalkan overlap sedikit, langsung True.
            - 1.0: hanya jika kedua bbox identik (perfect overlap), baru True.

    Returns:
        bool: True jika IoU (intersection over union) >= strictness, False jika tidak.
    """
    x1_a, y1_a, x2_a, y2_a = bbox1
    x1_b, y1_b, x2_b, y2_b = bbox2

    # Hitung area interseksi
    inter_x1 = max(x1_a, x1_b)
    inter_y1 = max(y1_a, y1_b)
    inter_x2 = min(x2_a, x2_b)
    inter_y2 = min(y2_a, y2_b)

    inter_width = max(0, inter_x2 - inter_x1)
    inter_height = max(0, inter_y2 - inter_y1)
    inter_area = inter_width * inter_height

    if inter_area == 0:
        return False

    # Hitung area union
    area_a = (x2_a - x1_a) * (y2_a - y1_a)
    area_b = (x2_b - x1_b) * (y2_b - y1_b)
    union_area = area_a + area_b - inter_area

    iou = inter_area / union_area

    return iou >= strictness


def merge_bbox(
    bbox1: Tuple[int, int, int, int],
    bbox2: Tuple[int, int, int, int]
) -> Tuple[int, int, int, int]:
    """
    Gabungkan dua bounding box menjadi satu bounding box yang mencakup keduanya.

    Args:
        bbox1 (Tuple[int, int, int, int]): Bounding box pertama dalam format (x1, y1, x2, y2).
        bbox2 (Tuple[int, int, int, int]): Bounding box kedua dalam format (x1, y1, x2, y2).

    Returns:
        Tuple[int, int, int, int]: Bounding box gabungan yang mencakup bbox1 dan bbox2.
    """
    x1_a, y1_a, x2_a, y2_a = bbox1
    x1_b, y1_b, x2_b, y2_b = bbox2

    x1 = min(x1_a, x1_b)
    y1 = min(y1_a, y1_b)
    x2 = max(x2_a, x2_b)
    y2 = max(y2_a, y2_b)

    return (x1, y1, x2, y2)
