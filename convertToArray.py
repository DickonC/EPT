import numpy as np
from PIL import Image
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt

def visualize_array(array, title="Speckle Pattern"):
    """
    A simple helper function to display the array as an image using Matplotlib.
    """
    plt.figure(figsize=(10, 8))
    # Using 'gray' colormap as it works well for both binary (0,1) and grayscale (0-255) arrays
    plt.imshow(array, cmap='gray')
    plt.title(f"{title} - Shape: {array.shape}")
    plt.axis('off')
    plt.show()

def convert_png_to_array(target_height, target_width, show_info=False, png_path=None):
    """
    Opens a PNG file, resizes it to a target resolution, and converts it
    into a binary NumPy array (0 for white, 1 for black).

    Args:
        target_height (int): The desired height of the output array. Defaults to 1200.
        target_width (int): The desired width of the output array. Defaults to 1920.
        show_info (bool): If True, prints array info and shows a visualization.

    Returns:
        np.array: The processed binary NumPy array, or None if no file is selected.
    """
    # Use a file dialog to let the user select a PNG file
    # root = Tk()
    # root.withdraw()  # Hide the small Tkinter window
    # png_path = filedialog.askopenfilename(
    #     title="Select PNG Speckle Pattern",
    #     filetypes=[("PNG files", "*.png")]
    # )

    # Exit if the user cancels the file dialog
    if not png_path:
        print("No file selected. Exiting.")
        return None

    try:
        # Open the image using Pillow and convert to grayscale ('L' mode)
        original_image = Image.open(png_path).convert('L')

        # --- RESIZING STEP ---
        # Resize the image to the target resolution using a high-quality filter (LANCZOS)
        resized_image = original_image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # --- CONVERSION TO BINARY ARRAY ---
        # Convert the resized image to a NumPy array.
        # Pixels with a brightness value <= 128 become 1 (black).
        # Pixels with a brightness value > 128 become 0 (white).
        final_array = (np.array(resized_image) <= 128).astype(np.uint8)

        # If the show_info flag is True, print details and visualize the result
        if show_info:
            print("\n--- Image Conversion Details ---")
            print(f"Original image dimensions: {original_image.size}")
            print(f"Target array dimensions: {target_width}x{target_height}")
            print(f"Final array shape: {final_array.shape}")
            
            # Show the final array as an image
            visualize_array(final_array, title="Final Speckle Array")

        return final_array

    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        return None

# --- Main execution block ---
# This part runs only when you execute this script directly.
# It demonstrates how to call the main function.
if __name__ == "__main__":
    # Call the function and request the info/visualization to be shown.
    # The resulting array is stored in the 'speckle_pattern' variable.
    print("Starting speckle pattern conversion...")
    speckle_pattern = convert_png_to_array(show_info=True)

    if speckle_pattern is not None:
        print("\nConversion complete. The array is ready to be used by other scripts.")
    else:
        print("\nConversion failed.")