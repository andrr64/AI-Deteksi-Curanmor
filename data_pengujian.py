from variables import VIDEO_MALAM, VIDEO_SIANG
from variables import aerox_malam, aerox_siang, beat_malam, beat_siang
from sysdata.wajah import authorized_faces

sample_1 = [[x, False] for x in VIDEO_SIANG] + [[x, True] for x in VIDEO_MALAM]
sample_2 = [[x['path'], False] for x in aerox_siang] + [[x['path'], True] for x in aerox_malam]

sample_1_aerox = [
        {
            'path': x,
            'malam': False,
            'dict_wajah': {'Andreas': authorized_faces['Andreas']},
            'dict_kendaraan': {
                'B5570FRL': ['Andreas'],
                'B5571FRL': [],
                'B5572FRL': [],
                'B5573FRL': [],
                'B5574FRL': [],
                'B4658SPA': [],
                'B4654SPA': [],
                'B4655SPA': [],
                'B4656SPA': [],
                'B4657SPA': [],
            }
        } for x in VIDEO_SIANG
    ] + [
        {
            'path': x,
            'malam': True,
            'dict_wajah': {'Andreas': authorized_faces['Andreas']},
            'dict_kendaraan': {
                'B5570FRL': ['Andreas'],
                'B5571FRL': [],
                'B5572FRL': [],
                'B5573FRL': [],
                'B5574FRL': [],
                'B4658SPA': [],
                'B4654SPA': [],
                'B4655SPA': [],
                'B4656SPA': [],
                'B4657SPA': [],
            }
        } for x in VIDEO_MALAM
    ]

sample_2_aerox = [
    {
        'path': x['path'],
        'malam': False,
        'dict_wajah': {x['pemilik']: authorized_faces[x['pemilik']]},
        'dict_kendaraan': {
            'B5570FRL': [x['pemilik']],
            'B5571FRL': [],
            'B5572FRL': [],
            'B5573FRL': [],
            'B5574FRL': [],
            'B4658SPA': [],
            'B4654SPA': [],
            'B4655SPA': [],
            'B4656SPA': [],
            'B4657SPA': [],
        }
    } for x in aerox_siang
] + [
    {
        'path': x['path'],
        'malam': True,
        'dict_wajah': {x['pemilik']: authorized_faces[x['pemilik']]},
        'dict_kendaraan': {
            'B5570FRL': [x['pemilik']],
            'B5571FRL': [],
            'B5572FRL': [],
            'B5573FRL': [],
            'B5574FRL': [],
            'B4658SPA': [],
            'B4654SPA': [],
            'B4655SPA': [],
            'B4656SPA': [],
            'B4657SPA': [],
        }
    } for x in aerox_malam
]

sample_3_beat = [
    {
        'path': x['path'],
        'malam': False,
        'dict_wajah': {x['pemilik']: authorized_faces[x['pemilik']]},
        'dict_kendaraan': {
            'B5570FRL': [],
            'B5571FRL': [],
            'B5572FRL': [],
            'B5573FRL': [],
            'B5574FRL': [],
            'B4658SPA': [x['pemilik']],
            'B4654SPA': [],
            'B4655SPA': [],
            'B4656SPA': [],
            'B4657SPA': [],
        }
    } for x in beat_siang
] + [
    {
        'path': x['path'],
        'malam': True,
        'dict_wajah': {x['pemilik']: authorized_faces[x['pemilik']]},
        'dict_kendaraan': {
            'B5570FRL': [],
            'B5571FRL': [],
            'B5572FRL': [],
            'B5573FRL': [],
            'B5574FRL': [],
            'B4658SPA': [x['pemilik']],
            'B4654SPA': [],
            'B4655SPA': [],
            'B4656SPA': [],
            'B4657SPA': [],
        }
    } for x in beat_malam
]