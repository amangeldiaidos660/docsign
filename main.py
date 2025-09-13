from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.documents import router as documents_router
from routers.pending_documents import router as pending_documents_router
from routers.signed_documents import router as signed_documents_router
from routers.sign import router as sign_router

from db.session import init_db

app = FastAPI(title="DocSign - Подписание PDF документов")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(documents_router)
app.include_router(pending_documents_router)
app.include_router(signed_documents_router)
app.include_router(sign_router)

@app.on_event("startup")
async def on_startup():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
