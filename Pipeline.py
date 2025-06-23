def Pipeline(typeAndInfo, number, pdf_path=None, camera=None):
    from pdf2image import convert_from_path
    import os
    from tkinter import Tk, filedialog
    from PDFtoPNG import convert_pdf_to_png
    from convertToArray import convert_png_to_array
    from Transformations import shifting, stretch, layer_cake, saveArrayAsPDF

    # Only ask for PDF path if not provided
    if pdf_path is None:
        pdf_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not pdf_path:
            print("No file selected. Exiting...")
            return None

    pngPath = convert_pdf_to_png(pdf_path)

    if pngPath is None:
        print("Failed to convert PDF to PNG. Exiting...")
        return None

    array = convert_png_to_array(target_width=camera.resolution_px[0], target_height=camera.resolution_px[1], png_path=pngPath)

    if array is None:
        print("Failed to convert PNG to array. Exiting...")
        return None

    if typeAndInfo[0] == "Stretch":
        stretchedArray = stretch(array, camera, x_stretch=typeAndInfo[1], y_stretch=typeAndInfo[2],png_path=pngPath)
        saveArrayAsPDF(stretchedArray, f"Stretch_X_{typeAndInfo[1]}_Y_{typeAndInfo[2]}_{number}.pdf")
        print(f"Stretch_X_{typeAndInfo[1]}_Y_{typeAndInfo[2]}_{number}.pdf complete")

    elif typeAndInfo[0] == "Layer Cake":
        layerCakeArray = layer_cake(array, camera, circle_radius_mm=typeAndInfo[1], circle_depth_mm=typeAndInfo[2],png_path=pngPath)
        saveArrayAsPDF(layerCakeArray, f"Layer_Cake_Radius_{typeAndInfo[1]}_Depth_{typeAndInfo[2]}_{number}.pdf")
        print(f"Layer_Cake_Radius_{typeAndInfo[1]}_Depth_{typeAndInfo[2]}_{number}.pdf complete")

    elif typeAndInfo[0] == "Shifting":
        shiftedArray = shifting(array, camera, x_shift_mm=typeAndInfo[1], y_shift_mm=typeAndInfo[2])
        saveArrayAsPDF(shiftedArray, f"Shift_X_{typeAndInfo[1]}_Y_{typeAndInfo[2]}_{number}.pdf")
        print(f"Shift_X_{typeAndInfo[1]}_Y_{typeAndInfo[2]}_{number}.pdf complete")

# Import the Camera
import cameraCalculations
from tkinter import Tk, filedialog

if __name__ == "__main__":
    # --- HELPER FUNCTIONS FOR USER INPUT ---
    def get_float_input(prompt):
        """Continuously asks the user for a float until valid input is given."""
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a number (e.g., 1.25 or 50).")

    def get_int_input(prompt, min_val=1):
        """Continuously asks the user for an integer until valid input is given."""
        while True:
            try:
                val = int(input(prompt))
                if val >= min_val:
                    return val
                else:
                    print(f"Please enter a number greater than or equal to {min_val}.")
            except ValueError:
                print("Invalid input. Please enter a whole number.")

    # --- 1. INITIAL SETUP (This part remains the same) ---
    import cameraCalculations
    from tkinter import Tk, filedialog

    TARGET_HEIGHT_PX = 1920
    TARGET_WIDTH_PX = int(TARGET_HEIGHT_PX * (150 / 200))
    specs = cameraCalculations.Camera(
        "KindleScreenSpecs",
        (TARGET_WIDTH_PX, TARGET_HEIGHT_PX),
        (150, 200)
    )

    # Get the source PDF path once at the beginning
    root = Tk()
    root.withdraw()
    pdf_path = filedialog.askopenfilename(
        title="Select the SOURCE Speckle Pattern PDF",
        filetypes=[("PDF files", "*.pdf")]
    )

    # --- 2. INTERACTIVE JOB CREATION ---
    if pdf_path:
        jobs_to_run = []
        job_counter = 0

        while True:
            print("\n--- Transformation Menu ---")
            print("1. Stretch")
            print("2. Layer Cake")
            print("3. Shifting")
            print("4. Finish and Generate PDFs")
            print("5. Exit")

            choice = input("Select an option (1-5): ")

            if choice == '1': # Stretch
                num_jobs = get_int_input("How many Stretch transformations do you want to create? ")
                for i in range(num_jobs):
                    print(f"\n--- Creating Stretch Job #{i+1} ---")
                    x_stretch = get_float_input("  Enter X-axis stretch factor (e.g., 1.1 for 10%): ")
                    y_stretch = get_float_input("  Enter Y-axis stretch factor (e.g., 1.0 for no change): ")
                    jobs_to_run.append(("Stretch", x_stretch, y_stretch))

            elif choice == '2': # Layer Cake
                num_jobs = get_int_input("How many Layer Cake transformations do you want to create? ")
                for i in range(num_jobs):
                    print(f"\n--- Creating Layer Cake Job #{i+1} ---")
                    radius = get_float_input("  Enter puck radius in mm (e.g., 37.5): ")
                    depth = get_float_input("  Enter puck depth in mm (e.g., 250): ")
                    jobs_to_run.append(("Layer Cake", radius, depth))

            elif choice == '3': # Shifting
                num_jobs = get_int_input("How many Shifting transformations do you want to create? ")
                for i in range(num_jobs):
                    print(f"\n--- Creating Shifting Job #{i+1} ---")
                    x_shift = get_float_input("  Enter X-axis shift in mm (right is positive): ")
                    y_shift = get_float_input("  Enter Y-axis shift in mm (down is positive): ")
                    jobs_to_run.append(("Shifting", x_shift, y_shift))

            elif choice == '4': # Finish and Generate
                if not jobs_to_run:
                    print("\nNo jobs created. Nothing to generate.")
                else:
                    print(f"\nFound {len(jobs_to_run)} jobs. Starting PDF generation...")
                    for i, job_info in enumerate(jobs_to_run):
                        Pipeline(job_info, i, pdf_path, specs)
                    print("\nAll jobs have been processed!")
                break # Exit the menu loop

            elif choice == '5': # Exit
                print("Exiting without generating PDFs.")
                break # Exit the menu loop
            
            else:
                print("Invalid choice. Please select an option from 1 to 5.")
    else:
        print("No source PDF file selected. Exiting.")