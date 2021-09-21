import numpy as np
import cv2
import gdal
import osr
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# ds: georefenced tiff image opened with gdal
def getCoordinates(ds, centroid):
    # open dataset
    xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()

    # x and y are pixel coordinates, get coordinate in space
    x = centroid[0]
    y = centroid[1]
    # stretches out x and y by the cell size, then
    # adds the corners of the image to get the location
    posX = px_w*x + rot1*y+ xoffset
    posY = rot2 * x + px_h * y + yoffset

    # shift to center of the pixel
    posX += px_w / 2.0
    posY += px_h / 2.0

    # get CRS from dataset 
    crs = osr.SpatialReference()
    crs.ImportFromWkt(ds.GetProjectionRef())

    # create lat/long crs with WGS84 datum
    crsGeo = osr.SpatialReference()
    crsGeo.ImportFromEPSG(3857) # 3857 is the EPSG id of lat/long crs 
    t = osr.CoordinateTransformation(crs, crsGeo)
    (long, lat, z) = t.TransformPoint(posX, posY)
    return (long, lat)

def getTotalArea(ds, px_w=None, px_h=None):
    # get width and height of pixels if it hasn't been given already
    if (px_w == None or px_h == None):
        _, px_w, _, _, _, px_h = ds.GetGeoTransform()

    # find a unit per cell size (m^2)
    area_per_cell = px_w * abs(px_h)

    # load in alpha channel
    raster_band = ds.GetRasterBand(4)
    
    # load info about size of raster
    xsize = raster_band.XSize
    ysize = raster_band.YSize

    # find all pixels in the image
    pixel_area = 0
    invis_area = 0
    delta = []
    old = 0
    for i in range(ysize):
        raster = ds.ReadAsArray(0, i, xsize, 1)
        rasterAlpha = raster[3,:,:]
        data_pixels = np.where(rasterAlpha != 0, 1, np.nan)
        pixel_area += np.nansum(data_pixels)
        
        delta.append(pixel_area-old)
        old = pixel_area

        invis_pixels = np.where(rasterAlpha != 255, 1, np.nan)
        invis_area += np.nansum(invis_pixels)
    
    print("Non-transparent pixels: ", pixel_area)
    print("Transparent pixels: ", invis_area)
    print("Missing pixels: ", xsize*ysize-(pixel_area+invis_area))
    total_area_raster = pixel_area*area_per_cell*10.764
    total_area_invis = invis_area*area_per_cell*10.764
    return total_area_raster

def getSegmentArea(ds, points, px_w = None, px_h = None):
    # get width and height of pixels if it hasn't been given already
    if (px_w == None or px_h == None):
        _, px_w, _, _, _, px_h = ds.GetGeoTransform()

    # find a unit per cell size (m^2)
    area_per_cell = px_w * abs(px_h)

    # create a polygon from our points and find its area
    x = [p[0] for p in points]
    y = [p[1] for p in points]
        
    pgon = Polygon(points)
    pixel_area = pgon.area

    # get total area in square meters
    total_area_segment = pixel_area*area_per_cell
    return total_area_segment
    
