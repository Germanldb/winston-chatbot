from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import chat, admin
from .database import engine, Base
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Winston & Harry Chatbot API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"DEBUG: Petición entrante: {request.method} {request.url}")
    response = await call_next(request)
    print(f"DEBUG: Respuesta enviada: {response.status_code}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# static and templates
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
