from typing import Dict, Any, List
from datetime import datetime
import re
import httpx
from core.settings import settings

def format_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp / 1000).strftime("%d.%m.%Y %H:%M:%S")

def extract_iin(subject: str) -> str:
    match = re.search(r'SERIALNUMBER=IIN(\d+)', subject)
    return match.group(1) if match else ""

async def process_signature_data(document_id: str, get_data: Dict[str, Any]) -> Dict[str, Any]:
    total_signatures = get_data.get("signaturesTotal", 0)
    print(f"\nВсего подписей: {total_signatures}")
    
    result = {
        "total_signatures": total_signatures,
        "signatures": []
    }
    
    signatures = get_data.get("signatures", [])
    async with httpx.AsyncClient() as client:
        for index, sig in enumerate(signatures, 1):
            signature_info = {
                "sign_id": sig["signId"],
                "signed_at": format_timestamp(sig["storedAt"]),
                "subject": sig["subject"],
                "iin": extract_iin(sig["subject"]),
                "key_usages": [
                    usage for usage in sig["keyUsages"] 
                    if usage in ["digitalSignature", "nonRepudiation"]
                ],
                "validity": {
                    "from": format_timestamp(sig["from"]),
                    "until": format_timestamp(sig["until"])
                },
                "issuer": sig["issuer"]
            }
            
            
            qr_response = await client.get(
                f"{settings.AUTH_BASE_URL}/api/{document_id}/signature/{sig['signId']}/qr",
                params={
                    "signFormat": 0,
                    "qrVersion": 25,
                    "qrLevel": "M"
                }
            )
            if qr_response.status_code == 200:
                qr_data = qr_response.json()
                
                
                if "qrCodes" in qr_data and qr_data["qrCodes"]:
                    signature_info["qr_codes"] = qr_data["qrCodes"]
                    signature_info["qr_info"] = {
                        "document_id": qr_data["documentId"],
                        "sign_id": qr_data["signId"],
                        "sign_type": qr_data["signType"],
                        "sign_format": qr_data["signFormat"],
                        "total_qr_codes": len(qr_data["qrCodes"])
                    }
            else:
                print(f"Failed to get QR codes: {qr_response.status_code} - {qr_response.text}")
            
            result["signatures"].append(signature_info)
            
            print(f"\n=== Информация о подписи #{index} ===")
            print(f"ID подписи: {signature_info['sign_id']}")
            print(f"Время подписания: {signature_info['signed_at']}")
            print(f"Подписант: {signature_info['subject']}")
            print(f"ИИН: {signature_info['iin']}")
            print(f"Тип подписи: {', '.join(signature_info['key_usages'])}")
            print(f"Действителен с: {signature_info['validity']['from']}")
            print(f"Действителен по: {signature_info['validity']['until']}")
            print(f"Издатель: {signature_info['issuer']}")
            print(f"Количество QR-кодов: {len(signature_info.get('qr_codes', []))}")
            print("=" * 40)
    
    return result