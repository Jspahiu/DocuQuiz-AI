from fpdf import FPDF
from PIL import Image

# Register DejaVu fonts once at module import so they are available for all PDFs.
FONTS_REGISTERED = False


class CustomPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global FONTS_REGISTERED
        if not FONTS_REGISTERED:
            # Try preferred folder first, then fallback to fonts/ttf
            regular_paths = [r'fonts\dejavu-sans-ttf-2.37\DejaVuSans.ttf', r'fonts\ttf\DejaVuSans.ttf']
            bold_paths = [r'fonts\dejavu-sans-ttf-2.37\DejaVuSans-Bold.ttf', r'fonts\ttf\DejaVuSans-Bold.ttf']

            added = False
            for p in regular_paths:
                try:
                    self.add_font('DejaVu', '', p, uni=True)
                    added = True
                    break
                except Exception:
                    continue

            added_bold = False
            for p in bold_paths:
                try:
                    self.add_font('DejaVu', 'B', p, uni=True)
                    added_bold = True
                    break
                except Exception:
                    continue

            if not (added or added_bold):
                raise FileNotFoundError(
                    'DejaVu font files not found. Expected at fonts/dejavu-sans-ttf-2.37/ or fonts/ttf/'
                )

            FONTS_REGISTERED = True

    def footer(self):
        # Set position at 15mm from bottom
        self.set_y(-15)
        # Use registered font (do not call add_font here)
        self.set_font('DejaVu', '', 8)
        # Add centered text
        self.cell(0, 10, 'DocuQuiz AI™ © 2025 DocuQuiz AI Inc. All rights reserved.', align='C')


class PDFCreator:
    def __init__(self, output_pdf_path, logo_path, text=""):
        self.output_pdf_path = output_pdf_path
        self.logo_path = logo_path  # Path to your logo image
        self.text = text

    def create_pdf_with_unicode_text(self):
        pdf = CustomPDF()
        # Set auto page break to leave room for footer
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

    # Fonts are registered at module import (register_fonts())

            # Place logo at left and title centered within the header area.
            # Use Pillow to read the actual image size so we can preserve aspect ratio
            # and compute the displayed image height in mm.
        # Header layout tweaks (tweak these to adjust sizing/spacing)
        logo_w = 65   # logo width in mm (bigger logos)
        logo_y = 6   # top position in mm
        title_margin = 75  # increased space to leave for larger logos on each side

        try:
            with Image.open(self.logo_path) as img:
                img_w_px, img_h_px = img.size
        except Exception:
            # If PIL can't open the image for some reason, fall back to a safe default
            img_w_px, img_h_px = (500, 500)

        # Compute displayed image height in mm keeping aspect ratio
        logo_h = logo_w * (img_h_px / img_w_px)
        
        # Add left logo
        left_logo_x = 6
        pdf.image(self.logo_path, x=left_logo_x, y=logo_y, w=logo_w)
        
        # Add right logo
        right_logo_x = pdf.w - logo_w - 6  # 6mm from right edge
        pdf.image(self.logo_path, x=right_logo_x, y=logo_y, w=logo_w)

        # Add larger title centered between logos, in bold
        title_font_size_pt = 24  # bigger title
        pdf.set_font('DejaVu', 'B', title_font_size_pt)
        # Convert font size from points to mm (1 pt = 0.352777... mm)
        title_font_size_mm = title_font_size_pt * 0.352777
        # Center title vertically relative to the logo
        title_y = logo_y + (logo_h / 2) - (title_font_size_mm / 2)
        
        # Calculate the width available for the title (page width minus margins for logos)
        title_width = pdf.w - (2 * title_margin)
        # Set position for centered title between logos
        pdf.set_xy(title_margin, title_y)
        pdf.cell(title_width, title_font_size_mm + 2, 'DocuQuiz AI', ln=True, align='C')

        # Move cursor below the logo (logo height + padding) so body text won't collide
        header_padding = 6  # smaller padding to reduce header size
        body_start_y = logo_y + logo_h + header_padding
        pdf.set_y(body_start_y)

        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, self.text)
        pdf.output(self.output_pdf_path)