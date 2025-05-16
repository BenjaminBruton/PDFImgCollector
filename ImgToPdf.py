import os
from PIL import Image
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkcalendar import DateEntry
from PyPDF2 import PdfMerger
from datetime import datetime

LOGO_PATH = "./img/TrueNorth_logo.png"

def get_folder_titles(root_dir, current_dir):
    """Use the child folder as title and the current folder as subtitle."""
    child_title = os.path.basename(os.path.dirname(current_dir))
    subtitle = os.path.basename(current_dir)
    return child_title, subtitle

def create_pdf_from_images(folder_path, output_pdf, main_title, sub_title):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg'))]
    image_files.sort()

    if not image_files:
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=10, w=50)

    pdf.set_font("Arial", style="B", size=16)
    pdf.ln(20)
    pdf.cell(200, 10, main_title, ln=True, align="C")
    pdf.set_font("Arial", style="", size=14)
    pdf.cell(200, 10, sub_title, ln=True, align="C")
    pdf.ln(10)

    file_title = f"{main_title} - {sub_title}"
    pdf.set_font("Arial", style="", size=12)
    pdf.cell(200, 10, file_title, ln=True, align="C")
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
    directories = [os.path.join(dp, d) for dp, dn, fn in os.walk(root_dir) for d in dn]
    total_dirs = len(directories)
    progress_value = 0
    progress_bar["maximum"] = total_dirs

    for dirpath, _, filenames in os.walk(root_dir):
        jpg_files = [f for f in filenames if f.lower().endswith(('.jpg', '.jpeg'))]
        if jpg_files:
            main_title, sub_title = get_folder_titles(root_dir, dirpath)
            file_title = f"{main_title} - {sub_title}.pdf"
            pdf_filename = os.path.join(dirpath, file_title)
            create_pdf_from_images(dirpath, pdf_filename, main_title, sub_title)
            progress_value += 1
            progress_bar["value"] = progress_value
            progress_bar.update()

        create_master_pdf(root_dir)
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

def create_master_pdf(root_dir):
    pdf_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".pdf") and not file.startswith("TNCG"):
                pdf_files.append(os.path.join(dirpath, file))

    if not pdf_files:
        print("No PDFs found to merge.")
        return

    master_title = os.path.basename(root_dir).split(' - ')[0]
    master_pdf_path = os.path.join(root_dir, f"TNCG {master_title} Master PDF.pdf")

    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=10, y=10, w=50)
    pdf.set_font("Arial", style="B", size=16)
    pdf.ln(20)
    pdf.cell(200, 10, master_title, ln=True, align="C")
    pdf.set_font("Arial", style="", size=14)
    pdf.cell(200, 10, "Merged PDFs", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", style="", size=12)
    for path in pdf_files:
        pdf.cell(200, 10, os.path.basename(path), ln=True, align="C")
    pdf.output("_temp_master_cover.pdf")

    merger = PdfMerger()
    merger.append("_temp_master_cover.pdf")
    for file in pdf_files:
        merger.append(file)
    merger.write(master_pdf_path)
    merger.close()
    os.remove("_temp_master_cover.pdf")
    print(f"Master PDF created: {master_pdf_path}")

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
