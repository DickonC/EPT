from pdf2image import convert_from_path
import os
from tkinter import Tk, filedialog

def convert_pdf_to_png(pdf_path=None):
    from pdf2image import convert_from_path
    import os
    from tkinter import Tk, filedialog
    
    # If no pdf_path provided, use file dialog
    if pdf_path is None:
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
        return None

    # Get the directory and filename without extension
    output_dir = os.path.dirname(pdf_path)
    filename = os.path.splitext(os.path.basename(pdf_path))[0]

    try:
        # Convert PDF to images #higher dpi is higher resolution
        images = convert_from_path(pdf_path, dpi=300)

        # Save first page as PNG and return the path
        output_path = os.path.join(output_dir, f"{filename}_page_1.png")
        images[0].save(output_path, "PNG")
        print(f"Saved page 1 as: {output_path}")

        print(f"\nConversion complete!")
        
        # Return the path to the saved PNG file
        return output_path

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    convert_pdf_to_png()

#to run this Type: python PDFtoPNG.py
#might need to be inside EPT directory

