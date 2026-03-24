from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth, dashboard
from database import engine
from models import Base
from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    return {"message": "API do Medidor de Energia"}

# Criar admin inicial
@app.on_event("startup")
def create_admin():
    db = Session(engine)
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        hashed = pwd_context.hash("admin123")
        admin = User(username="admin", hashed_password=hashed, role="admin")
        db.add(admin)
        db.commit()
    db.close()