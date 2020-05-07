import numpy as np
import h5py
from numba import jit


@jit(nopython=False)
def vectorize2d(map, nlon, nlat):
    """
    Vectorize 2d map into 1d vector array
    Args:
        nlon (int): number of longitudinal grid cells
        nlat (int): number of latitudinal grid cells
    Returns:
        ndarray: vectorized map in C order
        ndarray: 1d-2d mapper for longitude
        ndarray: 1d-2d mapper for latitude
    """
    vecmap = map.flatten()
    veclon = np.tile(np.arange(0, nlon), nlat)
    veclat = np.repeat(np.arange(0, nlat), nlon)
    return vecmap, veclon, veclat


@jit(nopython=True)
def getvecid(ilon, ilat, nlon):
    return ilat*nlon + ilon


@jit(nopython=False)
def constLocalPatch_nextxy(nextx, nexty, unitArea, patchArea,
                           name="network", undef=[-9, -10, -9999]):
    """
    Args:
        nextx (ndarray-like): nextx 2d array
        nexty (ndarray-like): nexty 2d array
        unitArea (ndarray): 2d array; unit catchment area of each grid points
        patchArea (float): reference value for local patch area
    Returns:
       NoneType
    Notes:
        patchArea is just reference-the unit catchment will be concatenated
        until sum of the cathment areas go beyond patchArea.
    ToDo:
        Optimize numba behavior
    """
    # create hdf5 dataset
    f = h5py.File("test_%s.hdf5" % name, "w")
    dt = h5py.vlen_dtype(np.int32)
    nlon = nextx.shape[1]
    nlat = nextx.shape[0]
    dset = f.create_dataset("vlen_int", (nlon*nlat,), dtype=dt)
    patches = []
    for ilat in range(nexty.shape[0]):
        for ilon in range(nextx.shape[0]):
            parea = unitArea[ilat, ilon]
            if parea in undef:
                # skip ocean
                continue
            lats = [ilat]
            lons = [ilon]
            if ilat in undef or ilon in undef:
                # skip river mouth/inland termination for further concatenation
                # because -9 and -10 are global values for all basin.
                # possible to implement with this algorithm, using basin.bin
                # by getting basin ID at [clat, clon], mask nextxy.
                continue
            clat = ilat  # current scope
            clon = ilon  # current scope
            flag = "up"
            upgrids = [[clat, clon]]  # initialize
            downgrids = [[clat, clon]]
            while parea < patchArea:
                if flag == "up":
                    upgrids_new = []
                    for ug in upgrids:
                        clat = ug[0]
                        clon = ug[1]
                        # search further upstream
                        ugs_next, parea_up = concatup_nextxy(clon, clat,
                                                             nextx, nexty,
                                                             unitArea, undef)
                        parea += parea_up
                        [lats.append(ug_next[0]) for ug_next in ugs_next]
                        [lons.append(ug_next[1]) for ug_next in ugs_next]
                        upgrids_new.extend(upgrids)
                        if not parea <= patchArea:
                            break
                    upgrids = upgrids_new
                    flag = "down"
                elif flag == "down":
                    for downgrid in downgrids:
                        # Fotran > C
                        dw_next = [nexty[downgrid[0], downgrid[1]]-1,
                                   nextx[downgrid[0], downgrid[1]]-1]
                    parea_down = unitArea[dw_next[0], dw_next[1]]
                    if parea_down in undef:
                        continue
                    parea += parea_down
                    if not isinstance(dw_next[0], list):
                        lats.append(dw_next[0])
                        lons.append(dw_next[1])
                        downgrids.append(dw_next)
                    else:
                        [lats.append(dg_next[0]) for dg_next in dw_next]
                        [lons.append(dg_next[1]) for dg_next in dw_next]
                        downgrids.extend(dw_next)
                    flag = "up"
            vecids = [getvecid(plon, plat, nlon)
                      for plon, plat in zip(lons, lats)]
            dset[getvecid(ilon, ilat, nlon)] = vecids
            patches.append(vecids)
            print(vecids)
    f.close()
    return patches


@jit(nopython=False)
def concatup_nextxy(clon, clat, nextx, nexty, unitArea, undef):
    upgrids = []
    parea = 0
    upgrids_cond = np.where(  # C > Fortran
                        (nextx == clon+1) * (nexty == clat+1))
    upnum = upgrids_cond[0].shape[0]
    for i in range(upnum):  # upstream
        nlat = upgrids_cond[0][i]  # next upstream point
        nlon = upgrids_cond[1][i]  # next upstream point
        assert nextx[nlat, nlon] == clon+1, \
            "%d is required from nextx, but got %d" \
            % (nextx[nlat, nlon], clon+1)
        assert nexty[nlat, nlon] == clat+1, \
            "%d is required from nexty, but got %d" \
            % (nexty[nlat, nlon], clat+1)
        uniarea = unitArea[nlat, nlon]
        if uniarea in undef:
            continue
        parea += uniarea
        upgrids.append([nlat, nlon])
    return upgrids, parea


def test():
    nextxy = np.fromfile("../missouri_03min/nextxy.bin",
                         np.int32).reshape(2, 276, 466)
    nextx = nextxy[0]
    nexty = nextxy[1]
    unitArea = np.fromfile("../missouri_03min/ctmare.bin",
                           np.float32).reshape(276, 466)
    patches = constLocalPatch_nextxy(nextx, nexty, unitArea, 500000000)
    return patches


if __name__ == "__main__":
    test()
