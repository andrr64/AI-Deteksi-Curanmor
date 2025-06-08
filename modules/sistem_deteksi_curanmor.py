from sysdata.kendaraan import authorized_vehicles
from datetime import datetime as dt, timedelta
from classes.orang import OrangOnline
from classes.motor import MotorOnline

class StatusKendaraan:
    def __init__(self, lp: str, list_nama: list[str]):
        self.status_didalam_frame = False
        self.status_diizinkan: bool | None = None
        self.status_maling = False 
        self.plat_nomor = lp
        self.list_orang_terotorisasi = list_nama
        self.terakhir_dilihat: dt | None = None
        self.list_orang_dilingkungan_5detik_terakhir: list[str] = []

    def __str__(self):
        return f'{self.plat_nomor} -> DF {self.status_didalam_frame} | DI {self.status_diizinkan} | MAL {self.status_maling} | {self.terakhir_dilihat}'
    
class SistemAntiCuranmor():
    def __init__(self, data_sistem: dict[str, list[str]], debug=False):
        self.data_status_kendaraan: dict[str, StatusKendaraan] = {}
        self.debug = debug
        for plat, list_orang_terotorisasi in data_sistem.items():
            self.data_status_kendaraan[plat] = StatusKendaraan(plat, list_orang_terotorisasi)  
            
    def update_terakhir_dilihat(self, plat: str):
        self.data_status_kendaraan[plat].terakhir_dilihat = dt.now()
        
    def set_status_didalam_frame(self, plat: str, status: bool):
        if self.data_status_kendaraan[plat].status_didalam_frame != True:
            self.data_status_kendaraan[plat].status_didalam_frame = status
        
    @property
    def is_ada_maling(self):
        return any(x.status_maling for x in self.data_status_kendaraan.values())