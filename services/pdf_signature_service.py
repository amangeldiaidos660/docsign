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
        self.label_x = 50  
        self.value_x = 250  
    

    def _extract_name(self, subject: str) -> str:
        cn_match = re.search(r'CN=([^,]+)', subject)
        given_match = re.search(r'GIVENNAME=([^,]+)', subject)
        
        parts = []
        if cn_match:
            parts.append(cn_match.group(1))
        if given_match and given_match.group(1).lower() not in ['null', 'none', '']:
            parts.append(given_match.group(1))
        
        return ' '.join(parts)

    async def add_signature_page(self, file_path: str, signature_data: Dict[str, Any]) -> str:
        original = PyPDF2.PdfReader(file_path)
        page_size = original.pages[0].mediabox
        
        signature_page = BytesIO()
        c = canvas.Canvas(signature_page, pagesize=(page_size[2], page_size[3]))
        c.setFont('Arial', 10)
        
        y = page_size[3] - 50 
        
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
            c.drawString(self.label_x, y, sig['subject']) 
            y -= 40
            
            c.drawString(self.label_x, y, "С:")
            c.drawString(self.value_x, y, sig['validity']['from'])
            y -= 20
            
            c.drawString(self.label_x, y, "По:")
            c.drawString(self.value_x, y, sig['validity']['until'])
            y -= 20
            
            c.drawString(self.label_x, y, "Издатель:")
            c.drawString(self.value_x, y, sig['issuer'])
            y -= 40
            
            if "qr_codes" in sig:
                x = 50
                for i, qr_code in enumerate(sig["qr_codes"][:4]):
                    qr_image = base64.b64decode(qr_code)
                    img = ImageReader(BytesIO(qr_image))
                    c.drawImage(img, x, y-100, width=100, height=100)
                    x += 120
                y -= 150
            
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