import numpy as np
import datetime
import os
import random


PATHFMT = "/project/uma_colin_gleason/yuta/SIRF/model/CaMa-Flood_v395b_20191030/inp/MCZ_15min/vic/ctl/Roff_15min_MCZ{0}.bin"
OUTFMT = "/project/uma_colin_gleason/yuta/SIRF/model/CaMa-Flood_v395b_20191030/inp/MCZ_15min/vic/{0:02d}/Roff_15min_MCZ{0}.bin"
DTYPE = np.float32
NLAT = 72
NLON = 152

def read_data(filepath):
    return np.fromfile(filepath, dtype=DTYPE).reshape(1, NLAT, NLON)


def read_data_from_fmt(year, month, day):
    date = datetime.datetime(year, month, day)
    datestr = date.strftime("%Y%m%d")
    return read_data(PATHFMT.format(datestr))


def save_data(ens, date):
    eNum = ens.shape[0]
    datestr = date.strftime("%Y%m%d")
    for i in range(eNum):
        outpath = OUTFMT.format(i, datestr)
        if not os.path.exists(os.path.dirname(outpath)):
            os.makedirs(os.path.dirname(outpath))
        ens[i].astype(DTYPE).flatten().tofile(outpath)


def shuffle_years(years, eNum=20):
    """
    Args:
        years (list)
    """
    ens = np.zeros([20, len(years)]).astype(np.int32)
    ens[0] = years
    for i in range(len(years)):
        ens[1::, i] = random.sample(years, eNum-1)
    # for i in range(1, eNum):
    #     ens[i] = random.sample(years, len(years))
    return ens


def make_ensemble(years, max_deviance=5):
    ens_years = shuffle_years(years)
    # for i in range(27, len(years)):
    for i in range(27, 28):
        ens_y = ens_years[:, i].tolist()
        sdate = datetime.datetime(ens_y[0], 1, 1)
        edate = datetime.datetime(ens_y[0], 12, 31)
        date = sdate
        while date <= edate:
            print(date)
            ens_data = np.concatenate([read_data_from_fmt(y, date.month, date.day) for y in ens_y], axis=0)
            ens_mean = ens_data.mean()
            ens_mean = np.where(ens_mean==0, 1e-8, ens_mean)
            ens_deviance = ens_data/ens_mean
            ens_deviance = np.where(ens_deviance > max_deviance, max_deviance, ens_deviance)
            new_ens = ens_data[0] * ens_deviance  # [0] is ctl
            save_data(new_ens, date)
            date = date + datetime.timedelta(days=1)


make_ensemble(np.arange(1979, 2010).astype(np.int32).tolist())
    
