import os
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog
import rasterio

tif = "sample.tif"

with rasterio.open(tif) as dataset:
    data = dataset.read(1)
    
    if dataset.nodata is not None:
        data = np.ma.masked_equal(data, dataset.nodata)
        
        
lowest = float(data.min())
highest = float(data.max())

print(lowest, highest)