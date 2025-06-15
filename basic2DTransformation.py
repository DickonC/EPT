import numpy as np
import matplotlib.pyplot as plt
from convertToArray import convert_png_to_binary_array, visualize_array

def shift(array, y_down, x_right):
    '''
    Shift Transformation, 
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


def stretch(array, x_stretch, y_stretch):
    '''
    This function stretches an array in the x and y direction using scipy.ndimage.zoom
    this bascially stretches with interpolation so when a pixel is stretched to a fraction of a pixel
    the pixel with the fraction is an average of its surrounding pixels (in short)
    
    Streth paramters are multiples so 2 would double 1.05 would be 5% increase
    '''
    from scipy.ndimage import zoom
    
    if array.ndim == 2:
        stretched_array = zoom(array, (y_stretch, x_stretch), order = 1)
        return stretched_array
    
    elif array.ndim == 3:
        stretched_array = zoom(array, (y_stretch, x_stretch, 1), order = 1)
        return stretched_array
    
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
    
    

def main():
    """
    array import.
    """
    # Convert PNG to binary array
    print("Select the PNG file to convert...")
    start_array = convert_png_to_binary_array(show_info=False, show_visualization=False)
    
    if start_array is None:
        print("No array was created. Exiting...")
        return
    
    # Print array dimensions
    print(f"\nArray dimensions: {start_array.shape}")
    print(f"Total pixels: {start_array.size}")

    choice = input(f"Enter the transformation you want to apply: \n Sh for Shift, St for Stretch: \n")

    if choice == "Sh":  
        #Apply Shift - (y_down, x_right)
        shiftYDown = 100
        shiftXRight = 400

        shifted_array = shift(start_array, shiftYDown, shiftXRight)

        #make Red One
        start_red_array = addRed(start_array)
        shifted_red_array = shift(start_red_array, shiftYDown, shiftXRight)

        #Display Comparison
        comparison(start_red_array, shifted_red_array)
    
    elif choice == "St":
        #Apply Stretch - (x_stretch, y_stretch)
        x_stretch = 1
        y_stretch = 2
        
        stretched_array = stretch(start_array, x_stretch, y_stretch)

        #make Red One
        start_red_array = addRed(start_array)
        stretched_red_array = stretch(start_red_array, x_stretch, y_stretch)

        #Display Comparison
        comparison(start_red_array, stretched_red_array)
        
        # Print array dimensions
        print(f"\n Strethed Array dimensions: {stretched_array.shape}")
        print(f"Total pixels: {stretched_array.size}")

if __name__ == "__main__":
    main()







