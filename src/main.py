import os
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth, dashboard, settings
from database import engine
from models import Base
from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext
from config import STATIC_DIR, TEMPLATES_DIR
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

# Garante que bancos existentes recebam colunas Tuya adicionadas ao modelo
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS tuya_device_id VARCHAR UNIQUE;"))
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS tuya_api_key VARCHAR;"))
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS tuya_api_secret VARCHAR;"))
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS tuya_token VARCHAR;"))
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS tuya_region VARCHAR DEFAULT 'us';"))
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS is_connected INTEGER DEFAULT 0;"))
    conn.execute(text("ALTER TABLE outlets ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now();"))
    conn.commit()

app = FastAPI()

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(settings.router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/")
def root():
    return {"message": "API do Medidor de Energia"}

@app.on_event("startup")
def create_admin():
    db = Session(engine)
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        # Puxa do .env, e se não achar nada, usa "admin123" como último recurso
        senha_inicial = os.getenv("INITIAL_ADMIN_PASSWORD")
        hashed = pwd_context.hash(senha_inicial)
        admin = User(username="admin", hashed_password=hashed, role="admin")
        db.add(admin)
        db.commit()
    db.close()