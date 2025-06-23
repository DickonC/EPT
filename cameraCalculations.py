import numpy as np

class Camera:
    """
    A class to store camera specifications and calculate related properties.
    This helps bridge the gap between pixel space and real-world physical space.
    """
    def __init__(self, name, resolution_px, fov_mm):
        """
        Initializes the Camera object with its core specifications.

        Args:
            name (str): The name of the camera system (e.g., "VIC-EDU").
            resolution_px (tuple): The camera's resolution in pixels (width, height).
                                   Example: (1200, 1920)
            fov_mm (tuple): The camera's physical field of view in mm (width, height).
                            Example: (150, 200)
        """
        if not (isinstance(resolution_px, (list, tuple)) and len(resolution_px) == 2):
            raise ValueError("resolution_px must be a tuple or list of (width, height)")
        if not (isinstance(fov_mm, (list, tuple)) and len(fov_mm) == 2):
            raise ValueError("fov_mm must be a tuple or list of (width, height)")

        self.name = name
        self.resolution_px = (resolution_px[0], resolution_px[1])
        self.fov_mm = (fov_mm[0], fov_mm[1])
        
        # Calculate derived properties upon initialization
        self.px_per_mm = self._pixels_per_mm()
        self.mm_per_px = self._mm_per_pixel()

    def _pixels_per_mm(self):
        """Calculates the number of pixels per millimeter for both axes."""
        px_per_mm_x = self.resolution_px[0] / self.fov_mm[0]
        px_per_mm_y = self.resolution_px[1] / self.fov_mm[1]
        return (px_per_mm_x, px_per_mm_y)

    def _mm_per_pixel(self):
        """Calculates the physical size (in mm) of a single pixel for both axes."""
        mm_per_px_x = self.fov_mm[0] / self.resolution_px[0]
        mm_per_px_y = self.fov_mm[1] / self.resolution_px[1]
        return (mm_per_px_x, mm_per_px_y)

    def get_recommended_speckle_size_mm(self, target_pixels=4):
        """Calculates the recommended physical speckle diameter."""
        # Use the larger mm_per_pixel value to ensure speckles are big enough for the lower-res axis
        worst_case_mm_per_px = max(self.mm_per_px)
        return target_pixels * worst_case_mm_per_px

    def __str__(self):
        """Provides a user-friendly string representation of the camera's properties."""
        rec_speckle_size = self.get_recommended_speckle_size_mm()
        return (
            f"--- Camera Specifications: {self.name} ---\n"
            f"Resolution:     {self.resolution_px[0]} x {self.resolution_px[1]} px\n"
            f"Field of View:  {self.fov_mm[0]} x {self.fov_mm[1]} mm\n"
            f"----------------------------------------------------\n"
            f"X-Axis Scale:   {self.px_per_mm[0]:.3f} px/mm  |  {self.mm_per_px[0]:.4f} mm/px\n"
            f"Y-Axis Scale:   {self.px_per_mm[1]:.3f} px/mm  |  {self.mm_per_px[1]:.4f} mm/px\n"
            f"----------------------------------------------------\n"
            f"Recommended Speckle Diameter (for ~4px coverage): ~{rec_speckle_size:.2f} mm\n"
        )

# Test the class directly
if __name__ == '__main__':
    # Define the specifications for the VIC-EDU system
    vic_edu_resolution = (1920, 1200)
    vic_edu_fov = (200, 150)

    # Create an instance of the Camera class
    vic_camera = Camera("VIC-EDU", vic_edu_resolution, vic_edu_fov)

    # Print the camera's properties using the __str__ method
    print(vic_camera)