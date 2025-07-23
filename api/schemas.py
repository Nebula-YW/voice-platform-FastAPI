from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class EchoRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class EchoResponse(BaseModel):
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    tax: Optional[float] = None


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    tax: Optional[float] = Field(None, ge=0)


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    full_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
