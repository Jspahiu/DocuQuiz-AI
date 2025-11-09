from PIL import Image
from fpdf import FPDF
import pytesseract

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
path = r"images\test.png"
# Simple image to string
text = pytesseract.image_to_string(Image.open(path))


pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, text)
pdf.output("data_sets\document.pdf")