#!/usr/bin/env python3
import argparse
import Metashape

parser = argparse.ArgumentParser(description='Extract an orthomosaic from its project file.')
parser.add_argument(
    "project_file",
    help="a path to a metashape project file (w/ a psx file ending)"
)
parser.add_argument(
    "out", help="the stitched orthomosaic"
)
args = parser.parse_args()

# open the metashape document
doc = Metashape.Document()
doc.open(args.project_file, read_only=True)

# find the correct chunk
for chunk in doc.chunks:
    if chunk.orthomosaic is not None:
        break

# export the orthomosaic
#chunk.exportRaster(args.out, split_in_blocks=True)
print(args.out)
compression = Metashape.ImageCompression()
#compression.tiff_compression = Metashape.ImageCompression.TiffCompressionLZW
compression.tiff_compression = Metashape.ImageCompression.TiffCompressionJPEG
compression.jpeg_quality = 75
compression.tiff_big = True
compression.tiff_compression = True

psize = chunk.orthomosaic.resolution
mapdim = [chunk.orthomosaic.width,  chunk.orthomosaic.height]
if max(mapdim)>65500:
    #define a new variable just in case the original resolution is needed
    psize = max(mapdim)/65500*psize
# line for exporting a smaller orthomosaic, would be nice to run this as an optional step
#chunk.exportRaster(args.out, projection=Metashape.OrthoProjection("EPSG::3857"), split_in_blocks=False, image_format=Metashape.ImageFormat.ImageFormatJPEG, image_compression=compression, resolution=psize)
chunk.exportRaster(args.out, projection=Metashape.OrthoProjection("EPSG::3857"), split_in_blocks=False, image_compression=compression, resolution=psize, white_background=False, save_alpha=True)
