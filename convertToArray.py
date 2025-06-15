from PIL import Image
import numpy as np
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt

def visualize_array(binary_array, title="Binary Array"):
    """
    Visualize the binary array as an image.
    Black pixels (1) will be shown as black, white pixels (0) as white.
    """
    plt.figure(figsize=(8, 8))
    plt.imshow(binary_array, cmap='binary', interpolation='nearest')
    plt.title(title)
    plt.axis('off')
    plt.show()

def crop_white_borders(binary_array):
    """
    Crop the white borders from the binary array.
    Returns the cropped array containing only the speckle pattern.
    """
    # Find rows and columns that contain at least one black pixel (1)
    rows_with_black = np.any(binary_array == 1, axis=1)
    cols_with_black = np.any(binary_array == 1, axis=0)
    
    # Find the first and last rows/columns with black pixels
    first_row = np.where(rows_with_black)[0][0]
    last_row = np.where(rows_with_black)[0][-1]
    first_col = np.where(cols_with_black)[0][0]
    last_col = np.where(cols_with_black)[0][-1]
    
    # Crop the array to these boundaries
    cropped_array = binary_array[first_row:last_row+1, first_col:last_col+1]
    
    # Make the array square by padding with white (0) if necessary
    max_dim = max(cropped_array.shape)
    square_array = np.zeros((max_dim, max_dim), dtype=np.uint8)
    
    # Calculate the position to place the cropped array in the center
    start_row = (max_dim - cropped_array.shape[0]) // 2
    start_col = (max_dim - cropped_array.shape[1]) // 2
    
    # Place the cropped array in the center of the square array
    square_array[start_row:start_row+cropped_array.shape[0], 
                start_col:start_col+cropped_array.shape[1]] = cropped_array
    
    return square_array

def convert_png_to_binary_array(show_info=True, show_visualization=True):
    """
    Convert a PNG file to a binary numpy array.
    
    Parameters:
    - show_info: If True, prints information about the conversion
    - show_visualization: If True, shows the visualization of the array
    
    Returns:
    - numpy array containing the binary image (1 for black, 0 for white)
    """
    # Create a Tkinter root window (but hide it)
    root = Tk()
    root.withdraw()

    # Open file dialog to select PNG file
    png_path = filedialog.askopenfilename(
        title="Select PNG file",
        filetypes=[("PNG files", "*.png")]
    )

    if not png_path:
        print("No file selected. Exiting...")
        return None

    try:
        # Open the image using PIL and convert to grayscale
        img = Image.open(png_path).convert('L')
        
        # Convert image to numpy array
        img_array = np.array(img)
        
        # Convert to binary (0s and 1s)
        # Values above 128 become 0 (white), below become 1 (black)
        binary_array = (img_array <= 128).astype(np.uint8)
        
        # Crop the white borders and make square
        cropped_array = crop_white_borders(binary_array)
        
        if show_info:
            # Print some information about the array
            print(f"\nImage converted successfully!")
            print(f"Original array shape: {img_array.shape}")
            print(f"Cropped array shape: {cropped_array.shape}")
            print(f"Number of 1s: {np.sum(cropped_array)}")
            print(f"Number of 0s: {cropped_array.size - np.sum(cropped_array)}")
            
            # Print a portion of the array from the middle
            print("\nMiddle portion of the binary array (50x50):")
            center_row = cropped_array.shape[0] // 2
            center_col = cropped_array.shape[1] // 2
            start_row = max(0, center_row - 25)
            start_col = max(0, center_col - 25)
            end_row = min(cropped_array.shape[0], center_row + 25)
            end_col = min(cropped_array.shape[1], center_col + 25)
            
            # Print the array portion
            for row in cropped_array[start_row:end_row]:
                print(''.join(map(str, row[start_col:end_col])))
        
        if show_visualization:
            visualize_array(cropped_array)
        
        return cropped_array

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # When running this file directly, show all information and visualization
    binary_array = convert_png_to_binary_array(show_info=True, show_visualization=True)
