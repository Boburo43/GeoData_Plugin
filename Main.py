import os
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import rasterio
import unreal


# Loop until valid file is selected
tif = None
while tif is None:
    tif = filedialog.askopenfilename(title="Select a Tif file", filetypes=[("TIF files", "*.tif"), ("TIFF files", "*.tiff"), ("All files", "*.*")])
    
    if not (tif.lower().endswith('.tif') or tif.lower().endswith('.tiff')):
        messagebox.showwarning("Wrong File Type", "Wrong file type chosen. Please select a TIF or TIFF file.")
        tif = None  # Reset to loop again
    else:
        break

filename = os.path.basename(tif)

# Ask user to select output folder
output_folder = filedialog.askdirectory(title="Select output folder for converted files")

if not output_folder:
    messagebox.showwarning("No folder selected", "No output folder was selected. Exiting.")
    exit()

def Get_Tif_Data():
    try:
        with rasterio.open(tif) as dataset:
            data = dataset.read(1)
            
            if dataset.nodata is not None:
                data = np.ma.masked_equal(data, dataset.nodata)
            
            lowest = float(data.min())
            highest = float(data.max())
            
            print(f"{filename}: low={lowest}, high={highest}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")

def convert_Tif_To_PNG(output_folder):
    try:
        # Use rasterio to read the TIF file instead of PIL
        with rasterio.open(tif) as dataset:
            data = dataset.read(1)  # Read first band
            
            # Handle no data values
            if dataset.nodata is not None:
                data = np.ma.masked_equal(data, dataset.nodata)
            
            # Normalize data to 0-255 range for PNG
            min_val = float(data.min())
            max_val = float(data.max())
            
            if max_val > min_val:
                normalized = ((data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            else:
                normalized = np.zeros_like(data, dtype=np.uint8)
            
            # Convert numpy array to PIL Image
            image = Image.fromarray(normalized, mode='L')
            image = image.convert("RGBA")
        
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, output_filename)
        
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        image.save(output_path, "PNG")
        
        print(f"Converted {filename} to {output_filename}")
        print(f"Saved to: {output_path}")
        messagebox.showinfo("Success", f"File saved to:\n{output_path}")
    except Exception as e:
        print(f"Error details: {str(e)}")
        messagebox.showerror("Error", f"Failed to convert file: {str(e)}")
    

Get_Tif_Data()
convert_Tif_To_PNG(output_folder)