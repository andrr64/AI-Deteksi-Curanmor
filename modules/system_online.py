from sysdata.kendaraan import authorized_vehicles
from datetime import datetime as dt, timedelta

INACTIVE = 1
ACTIVE = 2
THEFT = 3

class StatusKendaraan:
    def __init__(self, lp, peoples):
        self.status = INACTIVE
        self.plat_nomor = lp
        self.orang_terotorisasi = peoples
        self.terakhir_masuk: dt | None = None

class SistemManajemenKendaraan():
    def __init__(self, debug: bool = False):
        self.data_kendaraan: dict[str, StatusKendaraan] = {}
        self.debug = debug
        for lp, peoples in authorized_vehicles.items():
            self.data_kendaraan[lp] = StatusKendaraan(lp, peoples)
    
    def _debug_print(self, msg: str):
        if self.debug:
            print(f"[DEBUG] {msg}")
    
    @property
    def status_kemalingan(self):
        result = any(x.status == THEFT for x in self.data_kendaraan.values())
        self._debug_print(f"Status kemalingan: {result}")
        return result
    
    def status_menjadi_not_maling(self, plate: str):
        data_motor = self.data_kendaraan[plate]
        data_motor.terakhir_masuk = dt.now()
        data_motor.status = ACTIVE
        self._debug_print(f"{plate} diset menjadi NOT MALING (ACTIVE)")

    def status_menjadi_inactive(self, plate: str):
        d = self.data_kendaraan[plate]
        d.terakhir_masuk = dt.now()
        d.status = INACTIVE
        self._debug_print(f"{plate} diset menjadi INACTIVE")

    def status_menjadi_maling(self, plate: str):
        data_motor = self.data_kendaraan[plate]
        now = dt.now()
        self._debug_print(f"{plate} terdeteksi pada {now.strftime('%H:%M:%S')}")

        if data_motor.status == INACTIVE:
            data_motor.status = ACTIVE
            self._debug_print(f"{plate} sebelumnya INACTIVE → jadi ACTIVE")

        elif data_motor.status == ACTIVE:
            elapsed = now - data_motor.terakhir_masuk
            self._debug_print(f"{plate} sudah ACTIVE selama {elapsed.total_seconds():.2f} detik")
            if elapsed > timedelta(seconds=10):
                data_motor.status = THEFT
                self._debug_print(f"{plate} status berubah jadi THEFT!")

    def status_menjadi_active(self, plat: str):
        data_motor = self.data_kendaraan[plat]
        data_motor.status = ACTIVE
        data_motor.terakhir_masuk = dt.now()
        self._debug_print(f"{plat} diset menjadi ACTIVE")
