import cv2

def draw_rect(frame, bbox, color=(0, 255, 0), thickness=2):
    x1, y1, x2, y2 = map(int, bbox)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)


def draw_text(frame, text, org, font_scale=0.5, color=(255, 255, 255), thickness=1, bg_color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_width, text_height = text_size

    # Gambar background rectangle dulu
    x, y = org
    cv2.rectangle(frame, (x, y - text_height - 4), (x + text_width, y + 4), bg_color, -1)

    # Gambar teks
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
