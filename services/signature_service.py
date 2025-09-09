from typing import Dict, Any
import httpx
from datetime import datetime
from core.settings import settings
from services.signature_parser_service import process_signature_data
from services.pdf_signature_service import PDFSignatureService

async def add_signature(document_id: str, signature: str) -> Dict[str, Any]:
    payload = {"signType": "cms", "signature": signature}
    try:
        async with httpx.AsyncClient() as client:
            add_resp = await client.post(
                f"{settings.AUTH_BASE_URL}/api/{document_id}",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            if add_resp.status_code == 200:
                add_data = add_resp.json()
            else:
                add_data = {"status": add_resp.status_code, "text": add_resp.text}
            print(add_data)

            get_resp = await client.get(f"{settings.AUTH_BASE_URL}/api/{document_id}")
            if get_resp.status_code == 200:
                get_data = get_resp.json()
                signature_details = await process_signature_data(document_id, get_data)
                
            
            return {"add_result": add_data, "get_result": get_data}
    except Exception as e:
        print({"error": str(e)}) 
        return {"error": str(e)}
