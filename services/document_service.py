from typing import Dict, Any
import httpx
import base64
import os
from core.settings import settings

async def register_document(
    title: str,
    file_base64: str,
    signature: str,
    participant_count: int
) -> Dict[str, Any]:
    registration_payload = {
        "title": title,
        "description": "Подписание документа",
        "signType": "cms",
        "signature": signature,
        "settings": {
            "private": False,
            "signaturesLimit": participant_count + 1,
            "switchToPrivateAfterLimitReached": False,
            "unique": ["iin"],
            "strictSignersRequirements": False
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            registration_response = await client.post(
                f"{settings.AUTH_BASE_URL}/api",
                headers={"Content-Type": "application/json"},
                json=registration_payload
            )
            
            if registration_response.status_code == 200:
                registration_data = registration_response.json()
                # print(f"Registration response: {registration_data}")
                
                document_id = registration_data.get("documentId")
                if document_id:
                    document_content = base64.b64decode(file_base64)
                    
                    hash_fixation_response = await client.post(
                        f"{settings.AUTH_BASE_URL}/api/{document_id}/data",
                        headers={
                            "Content-Type": "application/octet-stream",
                            "Content-Length": str(len(document_content))
                        },
                        content=document_content
                    )
                    
                    # print(f"Hash fixation response: {hash_fixation_response.text}")
                    
                    os.makedirs("storage", exist_ok=True)
                    file_path = f"storage/{document_id}.pdf"
                    with open(file_path, "wb") as f:
                        f.write(document_content)
                    # print(f"File saved to: {file_path}")
                    
                    return {
                        "success": True,
                        "document_id": document_id,
                        "registration_data": registration_data,
                        "hash_fixation_response": hash_fixation_response.text,
                        "file_path": file_path
                    }
                else:
                    # print("No documentId in registration response")
                    return {"success": False, "error": "No documentId in registration response"}
            else:
                # print(f"Registration failed: {registration_response.status_code} - {registration_response.text}")
                return {"success": False, "error": f"Registration failed: {registration_response.status_code}"}
                
    except Exception as e:
        # print(f"Error during document registration: {e}")
        return {"success": False, "error": str(e)}
