from typing import Any, Dict
from urllib.parse import urljoin
import httpx
from fastapi import HTTPException
from core.settings import settings

async def authenticate(nonce: str, signature: str) -> Dict[str, Any]:
    base_url = settings.AUTH_BASE_URL.rstrip("/") + "/"
    endpoint_path = settings.AUTH_ENDPOINT_PATH.lstrip("/")
    full_url = urljoin(base_url, endpoint_path)

    payload = {
        "nonce": nonce,
        "signature": signature,
        "external": True,
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(full_url, json=payload, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка аутентификации: {response.text}"
                )
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Ошибка HTTP: {exc.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при выполнении запроса аутентификации: {str(e)}"
        )
