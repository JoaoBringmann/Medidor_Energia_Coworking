from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"))

class Outlet(Base):
    __tablename__ = "outlets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)
    tuya_device_id = Column(String, nullable=True, unique=True)
    tuya_api_key = Column(String, nullable=True)
    tuya_api_secret = Column(String, nullable=True)
    tuya_token = Column(String, nullable=True)
    tuya_region = Column(String, default="us", nullable=True)
    is_connected = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)