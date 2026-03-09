import sys
import os
import unreal
import numpy as np
import rasterio
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image
from scipy.ndimage import gaussian_filter

# --- MODULE PATH INJECTION ---
plugin_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir())
site_packages_path = os.path.normpath(os.path.join(plugin_dir, "Tif_Converter", "Content", "Python", "lib", "site-packages"))

if os.path.exists(site_packages_path):
    if site_packages_path not in sys.path:
        sys.path.insert(0, site_packages_path)
else:
    unreal.log_error(f"Tif_Converter: Could not find site-packages at {site_packages_path}.")

# ----------------------------

def tif_to_heightmap(should_smooth=False, smooth_amount=2):
    # Initialize Tkinter
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    tif_file = ""
    valid_file = False

    # --- THE STRICT VALIDATION LOOP ---
    while True:
        root.update() # Force UI refresh
        tif_file = filedialog.askopenfilename(
            title="Select a SQUARE Tif file",
            filetypes=[("TIF files", "*.tif"), ("TIFF files", "*.tiff")]
        )

        # If user cancels the file picker, exit the function immediately
        if not tif_file or tif_file == "":
            root.destroy()
            return (None, unreal.Vector2D(x=0.0, y=0.0))

        try:
            with rasterio.open(tif_file) as dataset:
                w = dataset.width
                h = dataset.height
                
                if w == h:
                    unreal.log(f"Tif_Converter: Valid square dimensions detected: {w}x{h}")
                    break # SUCCESS: Exit the loop and move to directory selection
                else:
                    # BLOCKER: Show error and do NOT 'break'. This forces the loop to restart.
                    messagebox.showerror(
                        "Dimension Error", 
                        f"REJECTED: File is {w}x{h}.\n\n"
                        "Unreal Landscapes must be square. Please select a different file."
                    )
                    unreal.log_warning(f"Tif_Converter: Rejected non-square file {w}x{h}")
                    
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read TIF:\n{str(e)}")
            root.destroy()
            return (None, unreal.Vector2D(x=0.0, y=0.0))

    # --- DIRECTORY SELECTION (Only reached if break is called) ---
    project_content_dir = unreal.Paths.project_content_dir()
    absolute_content_path = unreal.Paths.convert_relative_path_to_full(project_content_dir)

    chosen_disk_folder = filedialog.askdirectory(
        title="Select where to save the Heightmap PNG",
        initialdir=absolute_content_path
    )

    if not chosen_disk_folder:
        root.destroy()
        unreal.log_warning("Tif_Converter: Save cancelled by user.")
        return (None, unreal.Vector2D(x=0.0, y=0.0))

    # Logic to convert paths
    rel_path = os.path.relpath(chosen_disk_folder, absolute_content_path).replace("\\", "/")
    asset_path = "/Game" if rel_path == "." else f"/Game/{rel_path}"
   
    default_name = os.path.splitext(os.path.basename(tif_file))[0]
    if should_smooth:
        default_name += "_Smoothed"

    custom_name = simpledialog.askstring("Asset Name", "Enter name for the heightmap:", initialvalue=default_name)
    
    # Final cleanup of Tkinter before processing
    root.destroy()

    clean_name = custom_name.strip().replace(".", "_") if custom_name else default_name
    final_png_path = os.path.normpath(os.path.join(chosen_disk_folder, f"{clean_name}.png"))
    
    try:
        with rasterio.open(tif_file) as dataset:
            data = dataset.read(1)
            if dataset.nodata is not None:
                data = np.ma.masked_equal(data, dataset.nodata)
            
            tif_min = float(data.min())
            tif_max = float(data.max())
      
            if tif_max > tif_min:
                normalized = ((data - tif_min) / (tif_max - tif_min) * 65535.0).astype(np.uint16)
            else:
                normalized = np.zeros_like(data, dtype=np.uint16)
            
            if should_smooth:
                float_data = normalized.astype(np.float32)
                blurred_float = gaussian_filter(float_data, sigma=abs(smooth_amount))
                normalized = np.clip(blurred_float, 0, 65535).astype(np.uint16)

            Image.fromarray(normalized, mode='I;16').save(final_png_path)

        # Unreal Import Logic
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
            texture_asset.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
            texture_asset.set_editor_property('srgb', False)
            unreal.EditorAssetLibrary.save_asset(texture_full_path)

        os.system(f'echo {final_png_path}| clip')
        return (texture_asset, unreal.Vector2D(x=tif_min, y=tif_max))

    except Exception as e:
        unreal.log_error(f"Tif_Converter: Error during conversion: {str(e)}")
        return (None, unreal.Vector2D(x=0.0, y=0.0))