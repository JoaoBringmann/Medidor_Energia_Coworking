from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import get_db
from models import User, Session as Sess, Outlet, Credit
from influxdb import InfluxDBClient
from passlib.context import CryptContext
from config import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None or user.role != "admin":
        raise HTTPException(status_code=401, detail="Not authorized")
    return user

@router.get("/dashboard")
def dashboard(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(Sess).all()
    total_usage_time = sum([(s.end_time - s.start_time).total_seconds() / 3600 for s in sessions if s.end_time])
    total_credits = db.query(Credit).with_entities(Credit.amount).all()
    total_paid = sum([c[0] for c in total_credits])

    client = InfluxDBClient(host='influxdb', port=8086, database='consumo_watts')

    result = client.query('SELECT SUM(value) FROM consumo WHERE time > now() - 30d')
    total_energy = 0
    for point in result.get_points():
        total_energy = point['sum']

    outlets = db.query(Outlet).all()
    outlet_data = []
    for outlet in outlets:
        result = client.query(f'SELECT SUM(value) FROM consumo WHERE outlet = \'{outlet.id}\' AND time > now() - 30d')
        energy = 0
        for point in result.get_points():
            energy = point['sum']
        outlet_data.append({"name": outlet.name, "energy": energy})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_usage_time": total_usage_time,
        "total_energy": total_energy,
        "total_paid": total_paid,
        "outlet_data": outlet_data
    })

# Endpoints para CRUD
@router.post("/users")
def create_user(username: str, password: str, role: str = "user", db: Session = Depends(get_db), user=Depends(get_current_user)):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/reports")
def reports(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "grafana_url": "http://localhost:3000"
    })

# Similar para sessions, credits, outlets