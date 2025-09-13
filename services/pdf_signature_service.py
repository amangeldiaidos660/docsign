from typing import Dict, Any
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import base64
from io import BytesIO
import os
import re
from datetime import datetime
import pytz

FONT_PATH = os.path.join("static", "fonts", "arial.ttf")
pdfmetrics.registerFont(TTFont('Arial', FONT_PATH))

class PDFSignatureService:
    def __init__(self):
        self.margin = 80
        self.label_x = self.margin  
        self.value_x = self.margin + 200
        self.font_size = 10
    

    def _extract_name(self, subject: str) -> str:
        cn_match = re.search(r'CN=([^,]+)', subject)
        given_match = re.search(r'GIVENNAME=([^,]+)', subject)
        
        parts = []
        if cn_match:
            parts.append(cn_match.group(1))
        if given_match and given_match.group(1).lower() not in ['null', 'none', '']:
            parts.append(given_match.group(1))
        
        return ' '.join(parts)

    def _draw_wrapped_text(self, canvas, x: float, y: float, text: str, max_width: float) -> float:
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = canvas.stringWidth(test_line, 'Arial', self.font_size)
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            canvas.drawString(x, y, line)
            y -= 15
        
        return y

    async def add_signature_page(self, file_path: str, signature_data: Dict[str, Any]) -> str:
        original = PyPDF2.PdfReader(file_path)
        page_size = original.pages[0].mediabox
        page_width = float(page_size[2])
        page_height = float(page_size[3])
        
        signature_page = BytesIO()
        c = canvas.Canvas(signature_page, pagesize=(page_width, page_height))
        c.setFont('Arial', self.font_size)
        
        y = page_height - self.margin
        available_width = page_width - (2 * self.margin)
        
        for sig in signature_data["signatures"]:
            c.drawString(self.label_x, y, "Дата формирования подписи:")
            c.drawString(self.value_x, y, sig['signed_at'])
            y -= 20
            
            signer_name = self._extract_name(sig['subject'])
            c.drawString(self.label_x, y, "Подписал(-а):")
            c.drawString(self.value_x, y, signer_name)
            y -= 20
            
            if "digitalSignature" in sig["key_usages"]:
                c.drawString(self.label_x, y, "-Цифровая подпись:")
                c.drawString(self.value_x, y, "digitalSignature")
                y -= 20
            
            if "nonRepudiation" in sig["key_usages"]:
                c.drawString(self.label_x, y, "-Неотрекаемость:")
                c.drawString(self.value_x, y, "nonRepudiation")
                y -= 20
            
            c.drawString(self.label_x, y, "Субъект:")
            y -= 20
            y = self._draw_wrapped_text(c, self.label_x, y, sig['subject'], available_width)
            y -= 20
            
            c.drawString(self.label_x, y, "С:")
            c.drawString(self.value_x, y, sig['validity']['from'])
            y -= 20
            
            c.drawString(self.label_x, y, "По:")
            c.drawString(self.value_x, y, sig['validity']['until'])
            y -= 20
            
            c.drawString(self.label_x, y, "Издатель:")
            y -= 15
            issuer_width = available_width - (self.value_x - self.label_x)
            y = self._draw_wrapped_text(c, self.value_x, y, sig['issuer'], issuer_width)
            y -= 20
            
            if "qr_codes" in sig:
                qr_codes = sig["qr_codes"][:4]
                qr_size = 100
                qr_spacing = 120
                qrs_per_row = int((available_width - qr_size) // qr_spacing) + 1
                
                x = self.margin
                qr_row_y = y - qr_size
                
                for i, qr_code in enumerate(qr_codes):
                    if i > 0 and i % qrs_per_row == 0:
                        qr_row_y -= (qr_size + 20)
                        x = self.margin
                    
                    qr_image = base64.b64decode(qr_code)
                    img = ImageReader(BytesIO(qr_image))
                    c.drawImage(img, x, qr_row_y, width=qr_size, height=qr_size)
                    x += qr_spacing
                
                rows_used = (len(qr_codes) - 1) // qrs_per_row + 1
                y = qr_row_y - (20 if rows_used == 1 else 0)
            
            y -= 40
        
        c.save()
        
        output = PyPDF2.PdfWriter()
        for page in original.pages:
            output.add_page(page)
        
        signature_page.seek(0)
        sig_page = PyPDF2.PdfReader(signature_page)
        output.add_page(sig_page.pages[0])
        
        with open(file_path, "wb") as output_file:
            output.write(output_file)

        return file_path