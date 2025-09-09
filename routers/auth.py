from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
from urllib.parse import urljoin
from core.settings import settings
from pydantic import BaseModel
from services.auth_service import authenticate
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import SessionLocal
from db.models import User

router = APIRouter(prefix="", tags=["auth"])

class CheckPayload(BaseModel):
    nonce: str
    signature: str

subject_pattern = re.compile(r"(\w+)=(\".*?\"|[^,]+)")

def parse_subject(subject: str):
    result = {}
    for k, v in subject_pattern.findall(subject or ""):
        val = v.strip().strip('"')
        result[k] = val
    return result

def strip_prefix(value: str, prefix: str):
    if not value:
        return None
    return value[len(prefix):] if value.startswith(prefix) else value

def normalize_name(s: str):
    if not s:
        return None
    return " ".join([w.capitalize() for w in s.split()])

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@router.post("/get")
async def get_nonce():
    base_url = settings.AUTH_BASE_URL.rstrip("/") + "/"
    endpoint_path = settings.AUTH_ENDPOINT_PATH.lstrip("/")
    full_url = urljoin(base_url, endpoint_path)
    headers = {
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(full_url, headers=headers, json={})
            if response.status_code == 200:
                nonce = response.json().get("nonce")
                # print(nonce)
                return JSONResponse(content={"nonce": nonce})
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка при получении nonce: {response.text}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении nonce: {str(e)}"
        )

@router.post("/check")
async def check_signature(payload: CheckPayload, session: AsyncSession = Depends(get_session)):
    sigex = await authenticate(payload.nonce, payload.signature)
    parsed = parse_subject(sigex.get("subject"))
    iin_raw = sigex.get("userId")
    bin_raw = sigex.get("businessId")
    iin = strip_prefix(iin_raw, "IIN") if iin_raw else None
    bin_value = strip_prefix(bin_raw, "BIN") if bin_raw else None
    cn = parsed.get("CN")
    given = parsed.get("GIVENNAME")
    full_name = normalize_name((cn + (" " + given if given else "")) if cn else (given or None))
    org = parsed.get("O")
    organization = org.replace("\\", "").replace('"', '') if org else None

    if not iin:
        raise HTTPException(status_code=400, detail="iin is required from SIGEX")

    res = await session.execute(select(User).where(User.iin == iin))
    user = res.scalar_one_or_none()
    if user is None:
        user = User(iin=iin, bin=bin_value, full_name=full_name, organization=organization)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        user.bin = bin_value
        user.full_name = full_name
        user.organization = organization
        await session.commit()
    resp = JSONResponse(content={"user_id": user.id})
    resp.set_cookie(key="uid", value=str(user.id), httponly=True, samesite="lax", path="/")
    return resp
