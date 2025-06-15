from pdf2image import convert_from_path
import os
from tkinter import Tk, filedialog

def convert_pdf_to_png():
    # Create a Tkinter root window (but hide it)
    root = Tk()
    root.withdraw()

    # Open file dialog to select PDF file
    pdf_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        print("No file selected. Exiting...")
        return

    # Get the directory and filename without extension
    output_dir = os.path.dirname(pdf_path)
    filename = os.path.splitext(os.path.basename(pdf_path))[0]

    try:
        # Convert PDF to images #higher dpi is higher resolution
        images = convert_from_path(pdf_path, dpi=300)

        # Save each page as PNG
        for i, image in enumerate(images):
            output_path = os.path.join(output_dir, f"{filename}_page_{i+1}.png")
            image.save(output_path, "PNG")
            print(f"Saved page {i+1} as: {output_path}")

        print(f"\nConversion complete! {len(images)} pages converted.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    convert_pdf_to_png()

#to run this Type: python PDFtoPNG.py
#might need to be inside EPT directory

