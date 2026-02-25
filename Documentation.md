# GeoTIFF to Heightmap – Unreal Engine Plugin Documentation

## 1. Overview

Plugin Name: Tif Converter  
Current Version: 1.0.0  
Tested Unreal Engine Versions: 5.7+  
Supported Platform: Windows  

### Intended Audience
- Environment Artists  
- Technical Artists  
- Level Designers  

### Description

Tif Converter is an Unreal Engine plugin that converts GeoTIFF (.tif / .tiff) elevation data into properly formatted 16-bit grayscale PNG heightmaps for use with Unreal Landscapes.

The plugin:
- Normalizes elevation data to full 16-bit range (0–65535)
- Optionally applies Gaussian smoothing
- Automatically configures texture settings for landscape use
- Assists with correct landscape scaling

This ensures accurate terrain representation and prevents common heightmap import issues such as banding, gamma distortion, or incorrect compression.

---

## 2. Features

- Import .tif / .tiff elevation files
- Converts to 16-bit grayscale PNG
- Automatic min/max normalization
- Optional Gaussian smoothing (adjustable strength)
- Automatically sets:
  - Compression: TC_VectorDisplacementMap
  - sRGB: Disabled
- Generates scale values for correct landscape import

---

## 3. Installation

### 3.1 Requirements

- Unreal Engine 5.7 or newer  
  (Earlier versions may work but are not officially tested.)

### 3.2 Installation Steps

1. In file explorer copy the Tif_Converter folder into:

   <ProjectFolder>MyProject/Plugins/

2. Launch Unreal Engine.
3. Navigate to Edit → Plugins.
4. Locate Tif_Converter under the Importers category.
5. Enable the plugin.
6. Restart Unreal Engine (if prompted).

---

## 4. Getting Started

### 4.1 Verifying Installation

After restarting Unreal Engine:

1. Go to Edit → Plugins
2. Confirm that Tif_Converter is enabled.

### 4.2 Basic Workflow

1. Open the Editor Utility Widget provided by the plugin.
2. Choose whether to enable smoothing.
3. Set smoothing strength (if enabled).
4. Click Convert Tif to Png.
5. Select:
   - The source .tif file
   - Destination folder inside your Unreal project
   - A name for the output heightmap
6. Switch to Landscape Mode in Unreal.
7. Go to:
   Manage → New → Import from File
8. Select the generated PNG as the Heightmap.
9. Enter the overall landscape resolution into the plugin tool.
10. Click Get Scale.
11. Apply the generated X, Y and Z scale values in the Landscape settings.
12. Generate the landscape.

---

## 5. Technical Details

### Heightmap Conversion

- Output format: 16-bit grayscale PNG (I;16)
- Elevation data is normalized to full 0–65535 range.
- No-data values in the GeoTIFF are handled safely.
- Optional Gaussian smoothing is applied before final normalization.

### Texture Configuration

After import, the plugin automatically:

- Sets compression to TC_VectorDisplacementMap
- Disables sRGB

This ensures:
- No color compression artifacts
- No gamma correction distortion
- Maximum height precision

### Scale Calculation

The plugin calculates proper X, Y and Z scale values based on:
- Landscape resolution
- Heightmap size
- Elevation range (min/max values)

X and Y scale values are identical to preserve square landscape proportions.

Correct scaling ensures:
- Accurate terrain proportions
- Proper world elevation representation
- No stretching or compression artifacts

---

## 6. Example Use Case

Example: Importing real-world elevation data (LIDAR or GIS terrain)

1. Export elevation data as GeoTIFF.
2. Convert using Tif Converter.
3. Import into Unreal Landscape.
4. Apply generated scale.
5. Result: Accurate real-world terrain in Unreal Engine.

---

## 7. Limitations

- Only .tif and .tiff files are supported.
- Only rectangular GeoTIFF files are supported.
- Extremely large heightmaps may exceed Unreal Landscape size limits.
- Windows only (clipboard functionality is Windows-based).

---

## 8. Troubleshooting

Issue: Landscape appears flat  
Cause: Incorrect Z scale  
Solution: Recalculate scale using Get Scale

Issue: Terrain looks stepped or banded  
Cause: 8-bit PNG used  
Solution: Ensure 16-bit PNG output

Issue: Landscape distorted or stretched  
Cause: Resolution mismatch  
Solution: Verify heightmap resolution matches Landscape settings

Issue: Import fails  
Cause: Corrupted or unsupported TIF  
Solution: Re-export TIF using standard GeoTIFF format

---

## 9. Version History

Version 1.0.0  
Date: 2026-02-25  
Notes: Initial release