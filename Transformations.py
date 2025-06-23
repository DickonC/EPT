import numpy as np
import matplotlib.pyplot as plt
from convertToArray import convert_png_to_array, visualize_array
import math

def shifting(array, camera, y_shift_mm, x_shift_mm):
    """
    Shifts the array by a specified physical distance in millimeters.
    It converts the mm shift into a pixel shift using the camera's scale.
    Fills the empty space with a constant color (white).

    Args:
        array (np.array): The input 2D or 3D array.
        camera (Camera): An instance of the camera class with physical specs.
        y_shift_mm (float): The physical shift in the Y direction (down) in mm.
        x_shift_mm (float): The physical shift in the X direction (right) in mm.
    """

    import numpy as np
    from scipy.ndimage import map_coordinates,shift

    #Convert the physical shift in mm to a pixel shift
    y_down_px = y_shift_mm * camera.px_per_mm[1]
    x_right_px = x_shift_mm * camera.px_per_mm[0]


    if array.ndim == 2:
        # For a 2D binary array where 0 is white, we set cval=0.
        shifted_array = shift(array, shift=(y_down_px, x_right_px), mode='constant', cval=0)
    elif array.ndim == 3:
        # For a 3D RGB array where (255, 255, 255) is white, we set cval=255.
        shifted_array = shift(array, shift=(y_down_px, x_right_px, 0), mode='constant', cval=255)
    else:
        raise ValueError("Array must be 2D or 3D")
    return shifted_array

def stretch(array, camera, y_stretch, x_stretch, png_path=None):
    """
    Stretches an array by remapping coordinates
    This function stretches in pixel space

    Args:
        array (np.array): The input 2D or 3D (RGB) array.
        camera (Camera): An instance of the camera class (not actually used in this function)
        y_stretch (float): The stretch factor for the Y-axis.
        x_stretch (float): The stretch factor for the X-axis.
    """

    import numpy as np
    from scipy.ndimage import map_coordinates

    if not png_path:
        raise ValueError("A 'png_path' to the original speckle pattern is required for transformations.")

    # --- AUTO-SUPERSAMPLING LOGIC ---
    # Determine the supersample factor by finding the largest stretch amount
    # and rounding UP to the nearest whole number.
    supersample = math.ceil(max(x_stretch, y_stretch))
    if supersample < 1:
        supersample = 1
    # --- END OF AUTO-SUPERSAMPLING LOGIC ---

    final_height, final_width = array.shape[:2]

    if supersample > 1:
        # Calculate high-res dimensions while preserving aspect ratio.
        ss_height = int(final_height * supersample)
        ss_width = int(final_width * supersample)
        print(f"    - Stretch: auto-detected {supersample}x supersampling. Creating {ss_width}x{ss_height} temp array.")
        # Re-opens the original PNG to create a genuinely high-resolution source
        source_array = convert_png_to_array(target_height=ss_height, target_width=ss_width, png_path=png_path)
    else:
        # If no supersampling is needed, just use the provided array.
        source_array = array

    src_height, src_width = source_array.shape[:2]
    y_coords, x_coords = np.mgrid[0:final_height, 0:final_width]

    center_src_y, center_src_x = (src_height - 1) / 2.0, (src_width - 1) / 2.0
    center_final_y, center_final_x = (final_height - 1) / 2.0, (final_width - 1) / 2.0

    src_y = center_src_y + ((y_coords - center_final_y) / y_stretch)
    src_x = center_src_x + ((x_coords - center_final_x) / x_stretch)

    stretched_array = map_coordinates(source_array, np.array([src_y, src_x]), order=1, mode='constant', cval=0)
    return stretched_array

def layer_cake(array, camera, circle_radius_mm, circle_depth_mm, png_path=None):
    """
    Simulates a circular "puck" moving towards the camera, creating a perspective
    magnification and occlusion effect.

    Args:
        array (np.array): The input 2D or 3D (RGB) speckle pattern array.
        camera (Camera): An instance of the camera class with physical specs.
        circle_radius_mm (float): The physical radius of the puck in millimeters.
        circle_depth_mm (float): The distance the puck moves towards the camera in mm.

    Returns:
        np.array: The transformed array with the layer cake effect.
    """
    import numpy as np
    from scipy.ndimage import map_coordinates

    if not png_path:
        raise ValueError("A 'png_path' to the original speckle pattern is required for transformations.")

    # ... (The first part of your function calculating magnification is correct and stays the same)
    working_distance_mm = 500.0
    new_puck_distance_mm = working_distance_mm - circle_depth_mm
    if new_puck_distance_mm <= 0:
        raise ValueError("circle_depth_mm cannot be equal to or greater than the working distance.")
    magnification = working_distance_mm / new_puck_distance_mm

    # --- AUTO-SUPERSAMPLING LOGIC ---
    # Round the magnification UP to the nearest whole number.
    supersample = math.ceil(magnification)
    if supersample < 1:
        supersample = 1
    # --- END OF AUTO-SUPERSAMPLING LOGIC ---

    final_height, final_width = array.shape[:2]

    if supersample > 1:
        ss_height = int(final_height * supersample)
        ss_width = int(final_width * supersample)
        print(f"    - Layer Cake: auto-detected {supersample}x supersampling. Creating {ss_width}x{ss_height} temp array.")
        # Re-opens the original PNG to create a genuinely high-resolution source
        source_array = convert_png_to_array(target_height=ss_height, target_width=ss_width, png_path=png_path)
    else:
        source_array = array

    # ... (The rest of your function calculating coordinates and mapping is correct and stays the same)
    center_final_y, center_final_x = (final_height - 1) / 2.0, (final_width - 1) / 2.0
    y_coords_px, x_coords_px = np.mgrid[0:final_height, 0:final_width]

    apparent_radius_mm = circle_radius_mm * magnification
    x_coords_mm = (x_coords_px - center_final_x) * camera.mm_per_px[0]
    y_coords_mm = (y_coords_px - center_final_y) * camera.mm_per_px[1]
    dist_from_center_mm = np.sqrt(x_coords_mm**2 + y_coords_mm**2)
    puck_occlusion_mask = dist_from_center_mm <= apparent_radius_mm

    src_y = y_coords_px.copy()
    src_x = x_coords_px.copy()

    center_src_y, center_src_x = (source_array.shape[0] - 1) / 2.0, (source_array.shape[1] - 1) / 2.0

    src_y[puck_occlusion_mask] = center_src_y + ((y_coords_px[puck_occlusion_mask] - center_final_y) / magnification)
    src_x[puck_occlusion_mask] = center_src_x + ((x_coords_px[puck_occlusion_mask] - center_final_x) / magnification)

    transformed_array = map_coordinates(source_array, np.array([src_y, src_x]), order=1, mode='constant', cval=0)
    return transformed_array

def saveArrayAsPDF(array_to_save, pdf_filename):
    import os
    # Create the PDFs directory path relative to the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdfs_dir = os.path.join(script_dir, "PDFs")
    
    # Create the PDFs directory if it doesn't exist
    os.makedirs(pdfs_dir, exist_ok=True)
    
    # Create the full path for the PDF file
    full_pdf_path = os.path.join(pdfs_dir, pdf_filename)

    #height and width of the array in pixels.
    height, width = array_to_save.shape[:2]
    dpi = 300
    figsize_inches = (width / dpi, height / dpi)

    #Matlplotlib figure
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    #Display your array on the axes. `interpolation='none'` prevents blurring.
    ax.imshow(array_to_save, cmap='gray_r' if array_to_save.ndim == 2 else None, interpolation='none')

    #Save the figure to a PDF, removing any remaining whitespace.
    plt.savefig(full_pdf_path, bbox_inches='tight', pad_inches=0, dpi=dpi, format='pdf')
    plt.close(fig)

    print(f"Successfully saved PDF to: {full_pdf_path}")
    return None