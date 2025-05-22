from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.libro import LibroCreate, LibroOut
from app.services.libro_service import (
    create_libro,
    get_libro,
    update_libro,
    delete_libro
)
from app.core.database import get_db

router = APIRouter(prefix="/libros", tags=["libros"])

@router.post("/", response_model=LibroOut, status_code=status.HTTP_201_CREATED)
async def post_libro(libro: LibroCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await create_libro(db, libro)

@router.get("/{id}", response_model=LibroOut)
async def read_libro(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    resultado = await get_libro(db, id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return resultado

@router.put("/{id}", response_model=LibroOut)
async def put_libro(id: str, libro: LibroCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    actualizado = await update_libro(db, id, libro)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Libro no encontrado o sin cambios")
    return actualizado

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_libro_endpoint(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    exito = await delete_libro(db, id)
    if not exito:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return None
