# app/models/prestamo.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PrestamoModel(BaseModel):
    user_id: str = Field(..., example="609c5c8f8f1b2c00156e3a1d")
    libro_id: str = Field(..., example="609c5c8f8f1b2c00156e3a1e")
    fecha_prestamo: datetime = Field(..., example="2025-05-22T12:00:00Z")
    fecha_devolucion: datetime = Field(..., example="2025-06-05T12:00:00Z")
    fecha_real_devolucion: Optional[datetime] = Field(default=None, example="2025-06-01T10:00:00Z")
    devuelto: bool = Field(default=False, example=False)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "609c5c8f8f1b2c00156e3a1d",
                "libro_id": "609c5c8f8f1b2c00156e3a1e",
                "fecha_prestamo": "2025-05-22T12:00:00Z",
                "fecha_devolucion": "2025-06-05T12:00:00Z",
                "fecha_real_devolucion": "2025-06-01T10:00:00Z",
                "devuelto": True
            }
        }
class PrestamoInDB(PrestamoModel):
    id: Optional[str] = Field(default=None, alias="_id")
