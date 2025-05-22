from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from app.schemas.prestamo import PrestamoCreate, PrestamoOut
from app.services.prestamo_service import (
    create_prestamo,
    get_prestamo,
    list_prestamos_usuario,
    devolver_prestamo
)
from app.core.database import get_db

router = APIRouter(prefix="/prestamos", tags=["prestamos"])

@router.post("/", response_model=PrestamoOut, status_code=status.HTTP_201_CREATED)
async def post_prestamo(
    prestamo: PrestamoCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        return await create_prestamo(db, prestamo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=PrestamoOut)
async def read_prestamo(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await get_prestamo(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return doc

@router.get("/usuario/{user_id}", response_model=List[PrestamoOut])
async def read_prestamos_usuario(
    user_id: str,
    activos_only: bool = Query(False, description="Si es true, solo préstamos activos"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    prestamos = await list_prestamos_usuario(db, user_id, activos_only)
    return prestamos

@router.put("/{id}/devolver", response_model=PrestamoOut)
async def put_devolver(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await devolver_prestamo(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado o ya devuelto")
    return doc