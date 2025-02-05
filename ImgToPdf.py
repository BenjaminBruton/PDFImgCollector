import os
import img2pdf
from PIL import Image
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PyPDF2 import PdfMerger

# List of keywords to identify if the folder name is sufficient
KEYWORDS = [
    'ISD', 'Elementary', 'High School', 'Intermediate', 'Junior High', 'Middle School', 'Admin',
    'Transport', 'Stadium', 'Center', 'Training', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
    '9th', '10th', '11th', '12th'
]

# Path to the PNG logo
LOGO_PATH = "./img/TrueNorth_logo.png"  # Replace with the actual location if moved

def get_folder_titles(dirpath):
    """Determine main and subfolder titles based on folder name and parent directory."""
    folder_name = os.path.basename(dirpath)
    parent_name = os.path.basename(os.path.dirname(dirpath))

    # If the parent folder contains a keyword, use it as the main title
    if any(keyword in parent_name for keyword in KEYWORDS):
        return parent_name, folder_name

    # Otherwise, go one level higher for the main title
    grandparent_name = os.path.basename(os.path.dirname(os.path.dirname(dirpath)))
    if grandparent_name and not any(keyword in folder_name for keyword in KEYWORDS):
        return grandparent_name, folder_name

    return parent_name, folder_name  # Fallback to parent and current folder

def create_pdf_from_images(folder_path, output_pdf):
    """Creates a PDF from all JPEG images in a given folder with 4 images per page."""
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg'))]
    image_files.sort()

    if not image_files:
        return  # Skip if no images

    # Create the PDF and determine titles
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    main_title, sub_title = get_folder_titles(folder_path)

    # Add the logo image
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=10, w=50)  # Adjust position and size as needed

    # Add titles
    pdf.set_font("Arial", style="B", size=16)
    pdf.ln(20)  # Move below the logo
    pdf.cell(200, 10, main_title, ln=True, align="C")
    pdf.set_font("Arial", style="", size=14)
    pdf.cell(200, 10, sub_title, ln=True, align="C")
    pdf.ln(10)

    # Use the PDF filename as subtitle
    file_sub_title = os.path.splitext(os.path.basename(output_pdf))[0]
    pdf.set_font("Arial", style="", size=12)
    pdf.cell(200, 10, file_sub_title, ln=True, align="C")
    pdf.ln(10)

    # Add images
    images_per_page = 4
    images_on_page = 0
    x, y = 10, 60  # Initial position below the logo and titles
    page_width, page_height = pdf.w - 20, pdf.h - 70  # Adjust margins
    row_height = page_height / 2  # 2 rows per page
    col_width = page_width / 2   # 2 columns per page

    for img in image_files:
        img_path = os.path.join(folder_path, img)
        try:
            with Image.open(img_path) as image:
                pdf.image(img_path, x, y, col_width, row_height)

                images_on_page += 1
                x += col_width  # Move to next column
                if images_on_page % 2 == 0:
                    x = 10
                    y += row_height

                if images_on_page == images_per_page:
                    pdf.add_page()
                    x, y = 10, 60
                    images_on_page = 0
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    pdf.output(output_pdf, "F")
    print(f"PDF created: {output_pdf}")

def merge_pdfs(root_dir):
    """Merges all PDFs in the root directory into a master PDF."""
    merger = PdfMerger()
    pdf_files = []

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".pdf") and "TNCG" not in file:
                pdf_files.append(os.path.join(dirpath, file))
    
    pdf_files.sort()
    for pdf in pdf_files:
        merger.append(pdf)
    
    main_title, _ = get_folder_titles(root_dir)
    master_pdf_filename = os.path.join(root_dir, f"TNCG {main_title} Master PDF.pdf")
    merger.write(master_pdf_filename)
    merger.close()
    print(f"Master PDF created: {master_pdf_filename}")

def process_directory(root_dir, status_label, progress_bar):
    """Recursively navigates through directories and creates PDFs for folders containing JPEGs."""
    total_folders = sum([len(dirnames) for _, dirnames, _ in os.walk(root_dir)])
    progress_value = 0
    progress_bar["maximum"] = total_folders

    for dirpath, dirnames, filenames in os.walk(root_dir):
        jpg_files = [f for f in filenames if f.lower().endswith(('.jpg', '.jpeg'))]
        if jpg_files:
            folder_name = os.path.basename(dirpath)
            pdf_filename = os.path.join(dirpath, f"{folder_name}.pdf")
            create_pdf_from_images(dirpath, pdf_filename)
            progress_value += 1
            progress_bar["value"] = progress_value
            progress_bar.update()

    merge_pdfs(root_dir)
    status_label.config(text="Success!", fg="green")

def browse_directory(entry_field):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, folder_selected)

def start_processing(entry_field, status_label, progress_bar):
    directory = entry_field.get()
    if directory:
        process_directory(directory, status_label, progress_bar)

def create_gui():
    root = tk.Tk()
    root.title("CTA - Location Based Image Collection")
    root.geometry("400x300")

    tk.Label(root, text="Select Directory:", font=("Arial", 12)).pack(pady=10)
    entry_field = tk.Entry(root, width=40, font=("Arial", 10))
    entry_field.pack(pady=5)
    tk.Button(root, text="Browse", command=lambda: browse_directory(entry_field), font=("Arial", 12)).pack(pady=5)
    tk.Button(root, text="Submit", command=lambda: start_processing(entry_field, status_label, progress_bar), font=("Arial", 12)).pack(pady=10)
    
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    status_label = tk.Label(root, text="", font=("Arial", 12))
    status_label.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
