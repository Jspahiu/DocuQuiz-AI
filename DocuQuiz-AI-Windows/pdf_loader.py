import easyocr
from PIL import Image
from fpdf import FPDF
import pytesseract

class PDFLoader:
    def __init__(self, pdf_path, tesseract_path, output_pdf_path):
        self.pdf_path = pdf_path
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        #r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.pdf_path = pdf_path
        #r"images\test.png"
        self.output_pdf_path = output_pdf_path
        # data_sets\document.pdf

    # def extract_text(self):
    #     reader = easyocr.Reader(['en'])
    #     images = self._pdf_to_images()
    #     text = ""
    #     for image in images:
    #         result = reader.readtext(image)
    #         for res in result:
    #             text += res[1] + "\n"
    #     return text

    def extract_text_tesseract(self):
        text = pytesseract.image_to_string(Image.open(self.pdf_path))
        tokens_count = len(text) / 4
        return text, tokens_count
    
    def text_to_pdf(self, text):
        pdf = FPDF()
        pdf.add_page()
        # Add Unicode font (make sure fonts/DejaVuSans.ttf exists)
        pdf.add_font('DejaVu', '', r'fonts\dejavu-sans-ttf-2.37\DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, text)
        pdf.output(self.output_pdf_path)




# # If you don't have tesseract executable in your PATH, include the following:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# # Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
# path = r"images\test.png"
# Simple image to string



# pdf = FPDF()
# pdf.add_page()
# pdf.set_font("Arial", size=12)
# pdf.multi_cell(0, 10, text)
# pdf.output("data_sets\document.pdf")