from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict



class PrestamoBase(BaseModel):
    user_id: str = Field(..., example="usuario123")
    libro_id: str = Field(..., example="650a1b2c3d4e5f6789012345")
    fecha_prestamo: datetime = Field(..., example="2025-05-22T12:00:00Z")
    fecha_devolucion: datetime = Field(..., example="2025-06-05T12:00:00Z")


class PrestamoCreate(PrestamoBase):
    """
    Datos requeridos para crear un nuevo préstamo.
    """
    pass


class PrestamoInDB(PrestamoBase):
    id: Optional[str] = Field(None, alias="_id", example="650b2c3d4e5f678901234567")
    devuelto: bool = Field(False, description="¿Ya fue devuelto?")
    fecha_real_devolucion: Optional[datetime] = Field(None)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PrestamoOut(PrestamoInDB):
    """
    Modelo de salida para mostrar un préstamo al cliente.
    """
    pass
