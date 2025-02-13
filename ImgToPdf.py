import os
from PIL import Image
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# List of keywords to identify if the folder name is sufficient
KEYWORDS = [
    'Ele', 'HS', 'MS', 'Independent School District', 'District',
    'ISD', 'Elementary', 'High School', 'Intermediate', 'Junior High', 'Middle School', 'Admin',
    'Transport', 'Stadium', 'Center', 'Training', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
    '9th', '10th', '11th', '12th'
]

# Path to the PNG logo
LOGO_PATH = "./img/TrueNorth_logo.png"

def get_folder_titles(dirpath):
    """Determine main and subfolder titles based on folder name and parent directory."""
    folder_name = os.path.basename(dirpath)
    parent_name = os.path.basename(os.path.dirname(dirpath))

    import re

    if any(keyword in parent_name for keyword in KEYWORDS) or re.search(r'torium', parent_name, re.IGNORECASE):
        return parent_name, folder_name

    grandparent_name = os.path.basename(os.path.dirname(os.path.dirname(dirpath)))
    if grandparent_name and not any(keyword in folder_name for keyword in KEYWORDS):
        return grandparent_name, folder_name

    return parent_name, folder_name

def create_pdf_from_images(folder_path, output_pdf):
    """Creates a PDF from all JPEG images in a given folder."""
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg'))]
    image_files.sort()
    if not image_files:
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    main_title, sub_title = get_folder_titles(folder_path)

    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=10, w=50)

    pdf.set_font("Arial", style="B", size=16)
    pdf.ln(20)
    pdf.cell(200, 10, main_title, ln=True, align="C")
    pdf.set_font("Arial", style="", size=14)
    pdf.cell(200, 10, sub_title, ln=True, align="C")
    pdf.ln(10)
    
    file_sub_title = os.path.splitext(os.path.basename(output_pdf))[0]
    pdf.set_font("Arial", style="", size=12)
    pdf.cell(200, 10, file_sub_title, ln=True, align="C")
    pdf.ln(10)
    
    images_per_page = 4
    images_on_page = 0
    x, y = 10, 60
    page_width, page_height = pdf.w - 20, pdf.h - 70
    row_height = page_height / 2
    col_width = page_width / 2

    for img in image_files:
        img_path = os.path.join(folder_path, img)
        try:
            with Image.open(img_path) as image:
                pdf.image(img_path, x, y, col_width, row_height)
                images_on_page += 1
                x += col_width
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

def process_directory(root_dir, status_label, progress_bar):
    """Processes directories in hierarchical order."""
    directories = [os.path.join(dp, d) for dp, dn, fn in os.walk(root_dir) for d in dn]
    total_dirs = len(directories)
    progress_value = 0
    progress_bar["maximum"] = total_dirs

    for child_dir in sorted(os.listdir(root_dir)):
        child_path = os.path.join(root_dir, child_dir)
        if os.path.isdir(child_path):
            for grandchild_dir in sorted(os.listdir(child_path)):
                grandchild_path = os.path.join(child_path, grandchild_dir)
                if os.path.isdir(grandchild_path):
                    create_pdf_from_images(grandchild_path, os.path.join(grandchild_path, f"{grandchild_dir}.pdf"))
                    progress_value += 1
                    progress_bar["value"] = progress_value
                    progress_bar.update_idletasks()
            
            create_pdf_from_images(child_path, os.path.join(child_path, f"{child_dir}.pdf"))
            progress_value += 1
            progress_bar["value"] = progress_value
            progress_bar.update_idletasks()
    
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
