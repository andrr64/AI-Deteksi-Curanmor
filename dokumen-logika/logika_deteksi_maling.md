# Logika Deteksi Pencurian Kendaraan Bermotor

## 1. Pendahuluan

Dokumen ini menjelaskan logika formal yang diterapkan untuk mendeteksi potensi insiden pencurian kendaraan bermotor (motor). Sistem ini dirancang untuk mencapai deteksi yang akurat sekaligus meminimalkan *false positives*. **Penting untuk digarisbawahi bahwa sistem deteksi ini memerlukan plat nomor kendaraan yang terdaftar dan dapat dikenali agar fungsi deteksi dapat berjalan.**

---

## 2. Definisi Variabel Proposisional

Variabel proposisional biner berikut digunakan untuk merepresentasikan kondisi-kondisi yang relevan, dengan nilai $1$ untuk 'benar' (true) dan $0$ untuk 'salah' (false):

* **$V_R$**: Identitas kendaraan (plat nomor) **terdaftar dan dikenali** dalam basis data.
* **$M$**: Kendaraan melintasi batas geografis yang ditentukan. (Diimplementasikan sebagai posisi `ymax` kendaraan lebih besar dari `Y_REDLINE`).
* **$O_P$**: **Tidak ada** individu yang teridentifikasi sebagai pemilik atau pengguna berwenang di sekitar kendaraan.
* **$O_E$**: **Tidak ada** individu yang teridentifikasi di area lingkungan sekitar kendaraan.
* **$O_U$**: Terdapat individu yang teridentifikasi namun **tidak memiliki otorisasi** yang terdaftar untuk kendaraan tersebut.
* **$K_A$**: Kendaraan terdeteksi **hilang dari pandangan** atau tidak berada pada lokasi yang seharusnya.
* **$K_T$**: Kendaraan **tidak terdeteksi** selama lebih dari $2$ detik sejak kejadian kehilangan terdeteksi.
* **$I_E$**: Terdapat individu **tidak dikenal** di lingkungan sekitar kendaraan dalam rentang waktu $5$ detik sebelum kejadian kehilangan terdeteksi.
* **$N_P$**: **Tidak ada individu sama sekali** yang terdeteksi di lingkungan sekitar kendaraan dalam rentang waktu $5$ detik sebelum kejadian kehilangan terdeteksi.
* **$D$**: Peristiwa yang terdeteksi merupakan **indikasi pencurian** kendaraan bermotor.

---

## 3. Rumusan Logika Deteksi ($D$)

Deteksi pencurian kendaraan bermotor (**$D$**) diindikasikan jika kendaraan memiliki plat nomor yang terdaftar dan dikenali (**$V_R$**) **DAN** salah satu dari dua skenario utama berikut terpenuhi:

### Skenario 1: Pelintasan Batas Mencurigakan

Skenario ini terpicu jika:
* Kendaraan melintasi batas geografis ($M$) **$\land$**
* Tidak ada individu berwenang di sekitar kendaraan ($O_P$) **$\land$**
* ($\text{Tidak ada individu teridentifikasi di lingkungan } (O_E)$ **$\lor$** $\text{terdapat individu teridentifikasi tanpa otorisasi } (O_U)$).

**Notasi Logika Skenario 1:**
$$V_R \land (M \land O_P \land (O_E \lor O_U)) \to D$$

**Implementasi Kode Skenario 1:**
```python
if not data_motor.license_plate_is_none(): # Ini adalah prasyarat V_R
    # ... (kode inisialisasi dan pengambilan data)
    My = ymax > Y_REDLINE # M
    if My:
        # ... (pengambilan nama_terotorisasi)
        Op = not any(p_name in nama_terotorisasi for p_name in list_nama_di_lingkungan if p_name is not None)
        Oe = not any(p_name for p_name in list_nama_di_lingkungan if p_name is not None)
        Ou = any(p_name for p_name in list_nama_di_lingkungan if p_name is not None and p_name not in nama_terotorisasi)
        
        # Logika inti Skenario 1:
        if Op and (Oe or Ou):
            data_status_motor.status_maling = True
            # ... (aksi alarm)
```

### Skenario 2: Kehilangan Kendaraan Mencurigakan

Skenario ini terpicu jika:
* Kendaraan terdeteksi **hilang dari pandangan** ($K_A$) **$\land$**
* Kendaraan **tidak terdeteksi selama lebih dari $2$ detik** sejak kehilangan ($K_T$) **$\land$**
* ($\text{Terdapat individu tidak dikenal di lingkungan sebelum kehilangan } (I_E)$ **$\lor$** $\text{tidak ada individu sama sekali yang terdeteksi di lingkungan sebelum kehilangan } (N_P)$).

**Notasi Logika Skenario 2:**
$$V_R \land (K_A \land K_T \land (I_E \lor N_P)) \to D$$

**Implementasi Kode Skenario 2:**
```python
# ... (kode pengambilan recent_5_seconds_cache dan set_orang_5detik_terakhir)
for plat, data_status in sistem_manajemen_motor.data_status_kendaraan.items():
    # Prasyarat V_R diasumsikan karena motor ada di data_status_kendaraan
    
    Ka = (plat not in active_lp) and data_status.status_didalam_frame # K_A
    
    if Ka: # Jika Ka = True (motor hilang dari pandangan)
        elapsed = now - data_status.terakhir_dilihat # Waktu sejak terakhir terlihat
        Kt = elapsed > dt.timedelta(seconds=2) # K_T: Tidak terdeteksi > 2 detik

        if Kt: # Jika Kt = True (sudah 2 detik lebih hilang)
            # ... (pengambilan nama_terotorisasi)
            Ie = any(p_name is None or (p_name is not None and p_name not in nama_terotorisasi)
                    for p_name in set_orang_5detik_terakhir)
            Np = all(len(d_list) == 0 for d_list in recent_5_seconds_cache)
            
            # Logika inti Skenario 2:
            if Ie or Np: 
                data_status.status_maling = True
                # ... (aksi alarm)
            else:
                data_status.status_didalam_frame = False # Motor hilang dengan 'aman'
```

---

## 4. Prasyarat dan Kondisi Tambahan

### A. Prasyarat Plat Nomor ($V_R$)

Sistem ini **mensyaratkan** plat nomor kendaraan dapat dikenali (`not data_motor.license_plate_is_none()`). Jika plat nomor tidak terdaftar atau tidak dikenali, sistem tidak dapat melakukan evaluasi deteksi pencurian.

### B. Pengelolaan Cache Orang di Lingkungan

* **`cache_orang_dilingkungan_motor`**: Sebuah `deque` digunakan untuk menyimpan daftar nama orang yang terdeteksi di lingkungan setiap detik (dibatasi hingga $5$ detik terakhir).
    * Setiap elemen dalam `deque` adalah `list[str | None]`, di mana `None` merepresentasikan orang tak dikenal dan `[]` merepresentasikan tidak ada orang sama sekali yang terdeteksi pada detik tersebut.
    * Ukuran `deque` dibatasi hingga `FPS * 5` untuk mencakup riwayat $5$ detik penuh.
* **`set_orang_5detik_terakhir`**: Set ini dikumpulkan dari semua deteksi dalam $5$ detik terakhir, berisi nama-nama yang teridentifikasi dan/atau `None` untuk individu tak dikenal.

### C. Kondisi Filter `status_maling`

Pada kedua skenario (Skenario 1 dan Skenario 2), deteksi pencurian hanya akan dieksekusi jika motor tersebut **belum** ditandai sebagai `status_maling = True`. Ini mencegah sistem untuk terus-menerus memproses ulang motor yang sudah teridentifikasi sebagai objek curian.

### D. Penanganan `status_didalam_frame`

Variabel `data_status.status_didalam_frame` sangat penting, terutama untuk Skenario 2 ($K_A$).
* Variabel ini diatur `True` jika motor `plat_in_system` saat ini terdeteksi di `active_lp`.
* Pada Skenario 2, jika motor $K_A$ (hilang dari `active_lp`) tetapi $K_T$ (hilang lebih dari $2$ detik) tidak terpenuhi **ATAU** kondisi $I_E$ dan $N_P$ tidak terpenuhi, maka `data_status.status_didalam_frame` disetel ke `False`. Ini mengindikasikan bahwa motor tidak lagi dianggap dalam area pantau secara aktif atau telah "hilang dengan aman".

---

Bagaimana, Bro? Apakah simbol-simbol dan penjelasannya sudah lebih jelas dan sesuai dengan yang Anda inginkan?