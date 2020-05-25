import numpy as np
import netCDF4 as ncdf
import os
import datetime

sdate = datetime.datetime(1979,1,1)
datasrc = "../MCZ/cut_Mackenzie_dongmei.nc"
outdir = "./vic/"
prefix = "Roff_15min_MCZ"
suffix = "bin"
nsorder = "SN"

def read_nc(path, var="runoff"):
    data = ncdf.Dataset(path, mode="r")
    ret = data.variables[var][:]
    lon = data.variables["lon"][:]
    lat = data.variables["lat"][:]
    print("LAT: from {0:.3f} to {1:.3f}, ny {2}".format(lat[0], lat[-1], len(lat)))
    print("LON: from {0:.3f} to {1:.3f}, nx {2}".format(lon[0], lat[-1], len(lon)))
    return ret.filled(), lat, lon

def main(path, sdate, freq="D", var="runoff", nsorder="SN"):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    rof, lat, lon = read_nc(path, var=var)
    if lat[0] > lat[-1]:
        # ns
        if nsorder == "SN":
            print("NS order is converted to match %s" % nsorder)
            rof = rof[:, ::-1, :]
    else:
        # sn
        if nsorder == "NS":
            print("NS order is converted to match %s" % nsorder)
            rof = rof[:, ::-1, :]
    if freq == "D":
        print("Assuming input nc file is daily.")
        date = sdate
        print(rof.shape[0])
        for i in range(rof.shape[0]):
            print(date)
            cdate = date.strftime("%Y%m%d")
            outfile = os.path.join(outdir, "%s%s.%s" % (prefix, cdate, suffix))
            rof[i].astype(np.float32).flatten().tofile(outfile)
            date = date + datetime.timedelta(days=1)
    else:
        raise KeyError("freq %s is not implemented." % freq)

if __name__ == "__main__":
    main(datasrc, sdate, freq="D", var="runoff", nsorder=nsorder)
