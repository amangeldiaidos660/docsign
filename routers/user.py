from fastapi import APIRouter, Request, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import SessionLocal
from db.models import User
from datetime import datetime
import pytz
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="templates")

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

def format_datetime(dt: datetime, timezone_name: str = "Asia/Almaty") -> str:
    if not dt:
        return None
    try:
        tz = pytz.timezone(timezone_name)
        local_dt = dt.replace(tzinfo=pytz.UTC).astimezone(tz)
        return local_dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt.strftime("%d.%m.%Y %H:%M")

@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, user_id: int | None = None, uid: int | None = Cookie(default=None), session: AsyncSession = Depends(get_session)):
    if uid is not None and user_id is None:
        user_id = uid
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return templates.TemplateResponse("user_dashboard.html", {
        "request": request,
        "user": {
            "id": user.id,
            "iin": user.iin,
            "bin": user.bin,
            "full_name": user.full_name,
            "organization": user.organization,
            "email": user.email,
            "created_at": format_datetime(user.created_at)
        }
    })

class EmailPayload(BaseModel):
    email: EmailStr

@router.post("/email")
async def set_email(payload: EmailPayload, uid: int | None = Cookie(default=None), session: AsyncSession = Depends(get_session)):
    if uid is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    result = await session.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.email = payload.email
    await session.commit()
    return {"status": "ok"}

@router.get("/logout")
@router.get("/logout/")
async def logout():
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie(key="uid", path="/")
    return resp
