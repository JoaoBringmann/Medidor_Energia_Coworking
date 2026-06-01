import os
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from database import get_db
from models import User, Outlet
from config import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

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


@router.get("/settings")
def settings_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    outlets = db.query(Outlet).all()
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "outlets": outlets
    })


@router.post("/settings/outlet/add")
def add_outlet(
    request: Request,
    outlet_name: str = Form(...),
    outlet_location: str = Form(...),
    tuya_device_id: str = Form(...),
    tuya_region: str = Form(default="us"),
    tuya_api_key: str | None = Form(None),
    tuya_api_secret: str | None = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registramos a tomada para associação de consumo no dashboard. Controle de ligar/desligar não está habilitado."""
    existing_name = db.query(Outlet).filter(Outlet.name == outlet_name).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="Outlet com este nome já existe")

    # Verificar existência por Tuya device id (único)
    existing_device = db.query(Outlet).filter(Outlet.tuya_device_id == tuya_device_id).first()
    if existing_device:
        raise HTTPException(status_code=400, detail=f"Tuya device_id '{tuya_device_id}' já está registrado (Outlet id: {existing_device.id})")

    outlet = Outlet(
        name=outlet_name,
        location=outlet_location,
        tuya_device_id=tuya_device_id,
        tuya_api_key=tuya_api_key,
        tuya_api_secret=tuya_api_secret,
        tuya_region=tuya_region,
        is_connected=1
    )
    db.add(outlet)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Protege contra race conditions e fornece mensagem amigável
        raise HTTPException(status_code=400, detail=f"Erro de integridade ao salvar a tomada: {e.orig.pgerror if hasattr(e, 'orig') else str(e)}")
    db.refresh(outlet)

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "outlets": db.query(Outlet).all(),
        "message": f"Tomada '{outlet_name}' registrada com sucesso!"
    })


@router.post("/settings/outlet/delete/{outlet_id}")
def delete_outlet(
    outlet_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Tomada não encontrada")
    
    outlet_name = outlet.name
    db.delete(outlet)
    db.commit()
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "outlets": db.query(Outlet).all(),
        "message": f"Tomada '{outlet_name}' removida com sucesso!"
    })


@router.post("/settings/outlet/update/{outlet_id}")
def update_outlet(
    outlet_id: int,
    request: Request,
    outlet_name: str = Form(...),
    outlet_location: str = Form(...),
    tuya_device_id: str = Form(...),
    tuya_region: str = Form(default="us"),
    tuya_api_key: str | None = Form(None),
    tuya_api_secret: str | None = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Tomada não encontrada")
    
    outlet.name = outlet_name
    outlet.location = outlet_location
    outlet.tuya_device_id = tuya_device_id
    outlet.tuya_api_key = tuya_api_key
    outlet.tuya_api_secret = tuya_api_secret
    outlet.tuya_region = tuya_region
    outlet.is_connected = 1
    
    db.commit()
    db.refresh(outlet)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "outlets": db.query(Outlet).all(),
        "message": f"Tomada '{outlet_name}' atualizada com sucesso!"
    })


