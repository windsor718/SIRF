import numpy as np
from numba import jit
import json
import os


class Camap(object):

    def __init__(self):
        """
        Geo-mapping function tools for CaMa-Flood.
        """
        print("This is a toolkit to geomap dataset onto CaMa-Flood maps.\n"
              + "Register your json file first via .register(configjson).")

    def register(self, configjson):
        with open(configjson) as f:
            varDict = json.load(f)
        self.nlon = int(varDict["nlon"])
        self.nlat = int(varDict["nlat"])
        self.mapdir = str(varDict["mapdir"])
        self.west = float(varDict["west"])
        self.south = float(varDict["south"])
        self.hiresdir = str(varDict["hiresdir"])
        self.hirescat = varDict["hirescat"]  # same order as other hires lists
        self.hiresres = float(varDict["hiresres"])
        self.hiresnlon = varDict["hiresnlon"]  # same order as other hires lists
        self.hireswest = varDict["hireswest"]  # same order as other hires lists
        self.hiresnlat = varDict["hiresnlat"]  # same order as other hires lists
        self.hiressouth = varDict["hiressouth"]  # same order as other hires lists

    def mapgrid(self, lons, lats, *args,
                myfilter=None, buffer=1):
        """
        map coordinates onto a CaMa grid map.

        Args:
            lons (float): longitudes in decimal degrees
            lats (float): latitudes in decimal degrees
            args (tuple): additional arguments to pass to myfilter
            myfilter (function): additional filter to consider if any
            buffer (int): buffer for filtering (not used if myfilter=None)
        Returns:
            list: longitudinal model grid numbers in C style
            list: latitudinal model grid numbers in C style
        """
        hmaps = []
        for idx, cat in enumerate(self.hirescat):
            hmaps.append(self.read_hires(cat,
                                         self.hiresnlon[idx],
                                         self.hiresnlat[idx]))

        grids = batch_hiresmapper(hmaps, lons, lats,
                                  self.hireswest, self.hiressouth,
                                  self.hiresres, self.hiresnlon,
                                  self.hiresnlat, *args,
                                  myfilter=myfilter, buffer=buffer)
        outlons = [grid[0] for grid in grids]
        outlats = [grid[1] for grid in grids]
        errors = [grid[2] for grid in grids]
        return outlons, outlats, errors

    def read_hires(self, srcfile, nlon, nlat, zdim=2, dtype=np.int16):
        path = os.path.join(self.hiresdir, srcfile)
        hmap = np.memmap(path, dtype=dtype, mode="r",
                         shape=(zdim, nlat, nlon))
        return hmap


# @jit
def hiresmapper(hmaps, lon, lat, domains, *args,
                myfilter=None, buffer=5, idx=None):
    """
    extracting points based on a hiresolution map.
    Args:
        hmaps (list): numpy 2d ndarrays of hires data
        lon (float): longitude in decimal degrees
        lat (float): latitude in decimal degrees
        domains (list): latitudinal/longitudinal grid points as [lats, lons]
        *args (tuple): additional positional arguments to pass to myfilter
        myfilter (function): additional filter to consider if any
        buffer (int): buffer for filtering (not used if myfilter=None)
        idx (int): index number in case for the use in myfilter
    Returns:
        int: longitudial grid number in simulation grids
        int: latitudial grid number in simulation grids
        float: error in estimation
    Notes:
        simulation grids are upscaled model grid cells, not a hires one.
        myfilter function should return values to minimize,
        and takes at least following arguments:
        - clon: longitudinal grid number candidate
        - clat: latitudinal grid number candidate
        - ilon: longitudinal grid number candidate on hires map
        - ilat: latitudinal grid number candidate on hires map
        - idx: index number to access lits if passed
        function-dependent arguments should follow these as optional arguments.
    """

    for idx, domain in enumerate(domains):
        lons = np.array(domain[0])
        lats = np.array(domain[1])
        if lats[-1] < lat < lats[0] and lons[0] < lon < lons[-1]:
            latidx = np.argmin((lats-lat)**2)
            lonidx = np.argmin((lons-lon)**2)
            hmap = hmaps[idx]
            domidx = idx
        else:
            if idx == len(domains):
                print("cannot find point from hires map: lat {0:.03f} lon {0:.03f}"
                      .format(lat, lon))
            continue
    
    if myfilter is None:
        lonOut = hmap[0, latidx, lonidx] - 1 # F -> C
        latOut = hmap[1, latidx, lonidx] - 1 # F -> C
        error = 0
    else:
        error = 1e+20
        lonOut = np.nan
        latOut = np.nan
        for ilon in range(lonidx-buffer, lonidx+buffer):
            for ilat in range(latidx-buffer, latidx+buffer):
                try:
                    clonOut = hmap[0, ilat, ilon] - 1 # F-> C
                    clatOut = hmap[1, ilat, ilon] - 1 # F-> C
                except(IndexError):
                    continue
                cerror = myfilter(clonOut, clatOut, ilon, ilat,
                                  idx, domidx, *args)
                if cerror < error:
                    error = cerror
                    lonOut = clonOut
                    latOut = clatOut

    return lonOut, latOut, error


# @jit
def batch_hiresmapper(hmaps, lons, lats, hireswest, hiressouth, hiresres,
                      hiresnlon, hiresnlat, *args, myfilter=None, buffer=5):
    """
    batch wrapper for hiresmapper(*).
    Args:
        hmap (ndarray): numpy 2d ndarrays of hires data
        lons (list): longitudes in decimal degrees
        lats (list): latitudes in decimal degrees
        hireswest (list): west edges of hmap in decimal degrees
        hiressouth(list): south edges of hmap in decimal degrees
        hiresres (float): hires resolution in decimal degrees
        hiresnlon (list): numbers of longitudinal grid cells
        hiersnlat (list): numbers of latitudinal grid cells
        args : additional arguments to pass to myfilter
        myfilter (function): additional filter to consider if any
        buffer (int): buffer for filtering (not used if myfilter=None) 
    Returns:
        list: list of tuples (mdlLon, mdlLat) mapped onto grid cells
    Notes:
        simulation grids are upscaled model grid cells, not hires one
        filter function should return values to minimize.
    """
    domains = []
    for idx, w in enumerate(hireswest):
        s = hiressouth[idx]
        nlat = hiresnlat[idx]
        nlon = hiresnlon[idx]
        hireslons = np.arange(w, w+hiresres*(nlat+0.5), hiresres)
        # n to s
        hireslats = np.arange(s, s+hiresres*(nlon+0.5), hiresres)[::-1]
        domains.append([hireslons, hireslats])
    outputs = [hiresmapper(hmaps, lons[i], lats[i], domains, *args,
                           myfilter=myfilter, buffer=buffer, idx=i)
               for i in range(len(lons))]
    return outputs


def width_error(clon, clat, ilon, ilat, idx, domidx,
                refwidths, maxwidths, minwidths, widthmaps, hires):
    """
    calclate error between widths.

    Args:
        clon (int): longitudinal model grid number on upscaled map
        clat (int): latitudinal model grid number on upscaled map
        ilon (int): longitudinal grid number candidate on hires map
        ilat (int): latitudinal grid number candidate on hires map
        refwidths (list): list of reference widths
        widthmaps (list): memmapped arrays of a map (upscaled or hires)
        hires (bool): use hires map or not; must correspond with widthpath
    Return:
        float: normalized error
    """
    if hires:
        mdl_width = widthmaps[domidx][ilat, ilon]
    else:
        mdl_width = widthmaps[domidx][clat, clon]
    ref_width = refwidths[idx]
    error = ((mdl_width - ref_width)**2)**0.5 / ref_width
    if maxwidths[idx] < mdl_width or mdl_width < minwidths[idx]:
        error = 1e+20
    return error


def uparea_error(clon, clat, ilon, ilat, idx, domidx,
                 refupareas, upareamaps):
    """
    calculate error between upareas.

    Args:
        clon (int): longitudinal model grid number on upscaled map
        clat (int): latitudinal model grid number on upscaled map
        ilon (int): longitudinal grid number candidate on hires map
        ilat (int): latitudinal grid number candidate on hires map
        refupareas (list): list of reference uparea
        upareamaps (memmap): memmapped arrays of a map (upscaled or hires)
    Return:
        float: normalized error
    """
    mdl_uparea = upareamaps[domidx][clat, clon]
    ref_uparea = refupareas[idx]
    error = ((mdl_uparea - ref_uparea)**2)**0.5 / ref_uparea
    return error
