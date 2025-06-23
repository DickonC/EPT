import numpy as np
import matplotlib.pyplot as plt
from convertToArray import convert_png_to_array, visualize_array

def shift(array, y_down, x_right):
    '''
    Shift Transformation - wraps around the edges
    '''
    from scipy.ndimage import shift
    
    
    if array.ndim == 2:
        shifted_array = shift(array, shift=(y_down, x_right), mode = 'wrap')
        return shifted_array
    
    elif array.ndim == 3:
        shifted_array = shift(array, shift=(y_down, x_right,0), mode = 'wrap')
        return shifted_array
    
    else:
        raise ValueError("Array must be 2D or 3D")


def stretch(array, y_stretch, x_stretch):
    """
    Stretches an array by remapping coordinates, keeping the output dimensions the same.
    This simulates a camera with a fixed field of view looking at a stretching object.

    Args:
        array (np.array): The input 2D or 3D (RGB) array.
        y_stretch (float): The stretch factor for the Y-axis (e.g., 1.05 for 5%).
        x_stretch (float): The stretch factor for the X-axis.

    Returns:
        np.array: The stretched array, with the same shape as the input.
    """

    from scipy.ndimage import map_coordinates

    # Get the dimensions of the input array
    height, width = array.shape[:2]

    # 1. Create coordinate grids for the OUTPUT image. This is a grid of
    #    pixel locations for the final 1920x1200 image.
    y_coords, x_coords = np.mgrid[0:height, 0:width]

    # 2. Define the center of the stretch. We want to stretch from the middle.
    center_y, center_x = (height - 1) / 2.0, (width - 1) / 2.0

    # 3. Calculate the source coordinates for each output pixel.
    #    This is the "inverse mapping" step. To make the output look stretched,
    #    we sample the input from a "shrunken" set of coordinates.
    src_y = center_y + (y_coords - center_y) / y_stretch
    src_x = center_x + (x_coords - center_x) / x_stretch

    # Handle both grayscale (2D) and color (3D) images
    if array.ndim == 2:
        # For a 2D array, our source coordinates are just (y, x)
        source_coords = np.array([src_y, src_x])
        
        # 4. Use map_coordinates to create the new image.
        #    It takes the original array and the calculated source coordinates
        #    and handles all the interpolation automatically.
        #    'cval' defines the color for areas outside the original image (e.g., black for speckles).
        stretched_array = map_coordinates(array, source_coords, order=1, mode='constant', cval=0)
    
    elif array.ndim == 3:
        # For a 3D array, we need to apply the same transformation to each color channel.
        stretched_array = np.zeros_like(array)
        for i in range(array.shape[2]): # Loop through R, G, B channels
            source_coords = np.array([src_y, src_x])
            stretched_array[:, :, i] = map_coordinates(array[:, :, i], source_coords, order=1, mode='constant', cval=0)
    else:
        raise ValueError("Array must be 2D or 3D")
        
    return stretched_array

def layer_cake(array, camera, circle_radius_mm, circle_depth_mm):

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
    
    # 1. Get image and camera parameters
    height, width = array.shape[:2]
    cam_width_mm, cam_height_mm = camera.fov_mm
    working_distance_mm = 500.0  # From VIC-EDU lab manuals

    # 2. Create coordinate grids for the OUTPUT image in PIXELS
    y_coords_px, x_coords_px = np.mgrid[0:height, 0:width]
    
    # Define the center of the image in pixels
    center_y_px, center_x_px = (height - 1) / 2.0, (width - 1) / 2.0
    
    # 3. Calculate the distance of each pixel from the center (in pixels)
    dist_from_center_px = np.sqrt((x_coords_px - center_x_px)**2 + (y_coords_px - center_y_px)**2)
    
    # Convert the puck's physical radius to a pixel radius
    circle_radius_px = circle_radius_mm * camera.px_per_mm[0] # Using x-axis scale

    # 4. Create a "mask" to identify which pixels are part of the puck
    circle_mask = dist_from_center_px <= circle_radius_px

    # 5. Calculate the source coordinates for the remapping
    #    Initialize the source coordinates to be the same as the output coordinates (no change)
    src_y = y_coords_px.copy()
    src_x = x_coords_px.copy()
    
    # --- Perspective Math for the Puck Area ---
    # The new, closer distance of the puck's surface to the camera
    circle_distance_mm = working_distance_mm - circle_depth_mm
    
    # Calculate the magnification factor for the puck
    # Magnification = Original_Distance / New_Distance
    magnification = working_distance_mm / circle_distance_mm
    
    # Inside the puck mask, calculate the "shrunken" source coordinates
    # This "pulls" pixels from a smaller area of the original image, creating magnification.
    src_y[circle_mask] = center_y_px + (y_coords_px[circle_mask] - center_y_px) / magnification
    src_x[circle_mask] = center_x_px + (x_coords_px[circle_mask] - center_x_px) / magnification
    
    # 6. Apply the transformation using map_coordinates
    if array.ndim == 2:
        source_coords = np.array([src_y, src_x])
        # cval=0 fills the background with white (for a binary 0=white array)
        transformed_array = map_coordinates(array, source_coords, order=1, mode='constant', cval=0)
    elif array.ndim == 3:
        transformed_array = np.zeros_like(array)
        for i in range(array.shape[2]): # Loop through R, G, B
            source_coords = np.array([src_y, src_x])
            # For RGB, the background fill color is white (255)
            transformed_array[:, :, i] = map_coordinates(array[:, :, i], source_coords, order=1, mode='constant', cval=255)
    else:
        raise ValueError("Array must be 2D or 3D")
        
    return transformed_array
    
def comparison(originalWithRed, transformedWithRed):
    '''shows comparison of original and transformed array'''
    
    from matplotlib.gridspec import GridSpec
    #Grid Spec helps us with dynamically sizing the plots
    
    # Get the dimensions (height, width) of each image
    h1, w1 = originalWithRed.shape[:2]
    h2, w2 = transformedWithRed.shape[:2]

    # Create a figure
    fig = plt.figure(figsize=(12, 6))

    # Use GridSpec to define a grid with 1 row and 2 columns.
    # The 'width_ratios' argument makes the columns proportional to image widths.
    gs = GridSpec(1, 2, width_ratios=[w1, w2])
    
    #Original Array
    ax1 = fig.add_subplot(gs[0])
    ax1.imshow(originalWithRed, cmap='binary')
    ax1.set_title('Original Array')
    ax1.axis('off')
    
    #Transformed Array
    ax2 = fig.add_subplot(gs[1])
    ax2.imshow(transformedWithRed, cmap='binary')
    ax2.set_title('Transformed Array')
    ax2.axis('off')

    plt.tight_layout()
    plt.show()


def addRed(original):
    '''adds red to the original array'''
    #creates an array of the same size as the original
    height, width = original.shape
    
    #makes it all white
    rgb_array = np.full((height, width, 3), 255, dtype=np.uint8)
    
    #Where the binary array is 1, make it black
    rgb_array[original == 1] = [0,0,0]
    
    #Locating centres so we know where to add red
    centreX = width//2
    centreY = height//2
    
    #Setting an Offset so red isnt exactly on corners
    offset = 250 
    locations = [
        (centreY, centreX),                      # Center
        (offset, offset),                          # Top-Left
        (offset, width - 1 - offset),              # Top-Right
        (height - 1 - offset, offset),             # Bottom-Left
        (height - 1 - offset, width - 1 - offset)  # Bottom-Right
    ]
    
    #Create coordinate grids
    yy, xx = np.mgrid[:height, :width]
    
    red = [255,0,0]
    
    redRadius = 20
    
    
    for y, x in locations:
        # Calculate the distance of every pixel from the marker's center (y, x)
        distances = np.sqrt((xx - x)**2 + (yy - y)**2)
        
        # Create a "mask" for the circle (pixels where distance is close to the radius)
        # and a mask for the center dot (distance < 1).
        
        # circle_mask = (distances >= redRadius - 0.5) & (distances <= redRadius + 0.5)
        circle_mask = distances <= redRadius
        dot_mask = distances < 1
        
        # Use the masks to set the color to red, replacing what was there.
        rgb_array[circle_mask] = red
        rgb_array[dot_mask] = red
        
    return rgb_array
    
#Converting the numpy array back to a pdf file

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

def main():
    """
    array import.
    """
    # Convert PNG to binary array
    print("Select the PNG file to convert...")
    start_array = convert_png_to_array(show_info=False)
    
    if start_array is None:
        print("No array was created. Exiting...")
        return
    
    # Print array dimensions
    print(f"\nArray dimensions: {start_array.shape}")
    print(f"Total pixels: {start_array.size}")

    choice = input(f"Enter the transformation you want to apply: \n Sh for Shift, St for Stretch: \n")

    if choice == "Sh":  
        #Apply Shift - (y_down, x_right)
        shiftYDown = 200
        shiftXRight = 200

        shifted_array = shift(start_array, shiftYDown, shiftXRight)

        #make Red One
        start_red_array = addRed(start_array)
        shifted_red_array = shift(start_red_array, shiftYDown, shiftXRight)

        #Display Comparison
        comparison(start_red_array, shifted_red_array)
        saveArrayAsPDF(shifted_array,"Shifted.pdf")
    
    elif choice == "St":
        #Apply Stretch - (x_stretch, y_stretch)
        x_stretch = 3
        y_stretch = 3
        
        stretched_array = stretch(start_array, x_stretch, y_stretch)

        #make Red One
        start_red_array = addRed(start_array)
        stretched_red_array = stretch(start_red_array, x_stretch, y_stretch)

        #Display Comparison
        comparison(start_red_array, stretched_red_array)
        
        # Print array dimensions
        print(f"\n Strethed Array dimensions: {stretched_array.shape}")
        print(f"Total pixels: {stretched_array.size}")
        saveArrayAsPDF(stretched_array,"Stretched.pdf")

if __name__ == "__main__":
    main()







