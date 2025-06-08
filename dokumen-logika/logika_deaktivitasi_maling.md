
# Premis dan Objektivitas Sistem Deaktivasi Alarm Maling Motor


## 1. Objektivitas Sistem Deaktivasi

Tujuan utama dari sistem deaktivasi ini adalah untuk **menyaring dan memeriksa motor-motor yang saat ini berstatus pencurian ($D=1$)**. Apabila sebuah motor yang sebelumnya dicuri terdeteksi kembali memasuki area pemantauan yang aman (yaitu, berada di atas garis referensi/redline), maka status pencuriannya akan **secara otomatis dinonaktifkan ($D=0$)**. Sebaliknya, jika motor tersebut tidak kembali ke area aman, status pencuriannya akan dipertahankan ($D=1$).

---

## 2. Premis Logika Deaktivasi

Premis ini diterapkan untuk **semua motor yang memiliki status pencurian aktif ($D=1$)**.

**Jika** posisi vertikal maksimum motor ($y_{max}$, yaitu nilai tertinggi dari koordinat $y_1$ dan $y_2$ dari *bounding box* motor) **sudah berada di atas garis referensi/redline ($Y_{REDLINE}$)**, **maka** status pencurian motor tersebut akan disetel menjadi **tidak aktif ($D=0$)**.

**Notasi Logika Deaktivasi:**

Untuk setiap motor $X$ yang saat ini berstatus pencurian ($D_X=1$):
$$(y_{max}(X) > Y_{REDLINE}) \to (\neg D_X)$$

**Penjelasan:**

* $X$: Merujuk pada motor spesifik yang sedang dievaluasi.
* $D_X$: Status pencurian motor $X$ (di mana $1$ = pencurian, $0$ = bukan pencurian).
* $y_{max}(X)$: Koordinat $y$ tertinggi dari *bounding box* motor $X$ pada saat ini.
* $Y_{REDLINE}$: Garis batas atau ambang referensi di area pemantauan. Biasanya, area "aman" berada di atas garis ini.
* $\neg D_X$: Menunjukkan bahwa status pencurian motor $X$ menjadi *false* (dinonaktifkan).

---