import sys
import os
import unreal

# --- MODULE PATH INJECTION ---
# Automatically find the plugin's lib folder relative to this script's location
# This ensures that bundled dependencies work on any machine without manual installation
plugin_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir())
site_packages_path = os.path.normpath(os.path.join(plugin_dir, "Tif_Converter", "Content", "Python", "lib", "site-packages"))

if os.path.exists(site_packages_path):
    if site_packages_path not in sys.path:
        # Insert at index 0 to prioritize these versions over any local system versions
        sys.path.insert(0, site_packages_path)
        unreal.log(f"Tif_Converter: Successfully added dependencies to sys.path: {site_packages_path}")
else:
    unreal.log_error(f"Tif_Converter: Could not find site-packages at {site_packages_path}. Check plugin folder structure.")
# -----------------------------

import numpy as np
import rasterio
import tkinter as tk
from tkinter import filedialog, simpledialog 
from PIL import Image
from scipy.ndimage import gaussian_filter

def tif_to_heightmap(should_smooth=False, smooth_amount=2):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    tif_file = filedialog.askopenfilename(
        title="Select a Tif file",
        filetypes=[("TIF files", "*.tif"), ("TIFF files", "*.tiff")]
    )

    if not tif_file:
        root.destroy()
        return (None, unreal.Vector2D(x=0.0, y=0.0))

    
    project_content_dir = unreal.Paths.project_content_dir()
    absolute_content_path = unreal.Paths.convert_relative_path_to_full(project_content_dir)

    chosen_disk_folder = filedialog.askdirectory(
        title="Select where to save the Heightmap PNG",
        initialdir=absolute_content_path
    )

    if not chosen_disk_folder:
        root.destroy()
        unreal.log_warning("No destination folder selected.")
        return (None, unreal.Vector2D(x=0.0, y=0.0))

    # Convert absolute OS path to Unreal internal asset path format
    rel_path = os.path.relpath(chosen_disk_folder, absolute_content_path).replace("\\", "/")
    
    if rel_path == ".":
        asset_path = "/Game"
    else:
        asset_path = f"/Game/{rel_path}"
   
    default_name = os.path.splitext(os.path.basename(tif_file))[0]
    if should_smooth:
        default_name += "_Smoothed"

    custom_name = simpledialog.askstring("Asset Name", "Enter name for the heightmap:", initialvalue=default_name)
    root.destroy()

    clean_name = custom_name.strip().replace(".", "_") if custom_name else default_name
    final_png_path = os.path.normpath(os.path.join(chosen_disk_folder, f"{clean_name}.png"))
    
    try:
        with rasterio.open(tif_file) as dataset:
            data = dataset.read(1)
            # Use masked array to prevent NoData values from skewing normalization
            if dataset.nodata is not None:
                data = np.ma.masked_equal(data, dataset.nodata)
            
            tif_min = float(data.min())
            tif_max = float(data.max())
      
            # Map height values to full 16-bit range (0-65535) for maximum precision
            if tif_max > tif_min:
                normalized = ((data - tif_min) / (tif_max - tif_min) * 65535.0).astype(np.uint16)
            else:
                normalized = np.zeros_like(data, dtype=np.uint16)
            
           
            if should_smooth:
                float_data = normalized.astype(np.float32)
                blurred_float = gaussian_filter(float_data, sigma=smooth_amount)
                normalized = np.clip(blurred_float, 0, 65535).astype(np.uint16)

            # 'I;16' mode ensures the PNG is saved as true 16-bit grayscale
            Image.fromarray(normalized, mode='I;16').save(final_png_path)

        
        import_task = unreal.AssetImportTask()
        import_task.filename = final_png_path
        import_task.destination_path = asset_path
        import_task.destination_name = clean_name
        import_task.replace_existing = True
        import_task.automated = True
        import_task.save = True

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([import_task])
        
        texture_full_path = f"{asset_path}/{clean_name}"
        texture_asset = unreal.load_object(None, texture_full_path)
        
        if texture_asset:
            # VectorDisplacementMap prevents 8-bit compression, preserving 16-bit height detail
            texture_asset.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
            texture_asset.set_editor_property('srgb', False)
            unreal.EditorAssetLibrary.save_asset(texture_full_path)
            unreal.EditorAssetLibrary.sync_browser_to_objects([texture_full_path])

        # Copy file path to clipboard for easy pasting into Landscape Import UI
        os.system(f'echo {final_png_path}| clip')
        unreal.log(f"Imported to: {asset_path}")
        return (texture_asset, unreal.Vector2D(x=tif_min, y=tif_max))

    except Exception as e:
        unreal.log_error(f"Failed to convert file: {str(e)}")
        return (None, unreal.Vector2D(x=0.0, y=0.0))