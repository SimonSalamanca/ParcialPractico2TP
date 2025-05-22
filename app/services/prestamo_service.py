from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.prestamo import PrestamoCreate
from app.models.prestamo import PrestamoInDB
from bson import ObjectId
from datetime import datetime

MAX_PRESTAMOS_ACTIVOS = 3

async def create_prestamo(db: AsyncIOMotorDatabase, prestamo: PrestamoCreate):
    # Verificar si el usuario ya tiene el máximo de préstamos activos
    activos = await count_prestamos_usuario(db, prestamo.user_id, activos_only=True)
    if activos >= MAX_PRESTAMOS_ACTIVOS:
        raise ValueError("El usuario ha alcanzado el número máximo de préstamos activos.")

    prestamo_dict = prestamo.dict()
    prestamo_dict["devuelto"] = False
    result = await db["prestamos"].insert_one(prestamo_dict)
    return str(result.inserted_id)

async def list_prestamos_usuario(db: AsyncIOMotorDatabase, user_id: str, activos_only: bool = False):
    filtro = {"user_id": user_id}
    if activos_only:
        filtro["devuelto"] = False
    cursor = db["prestamos"].find(filtro)
    return [PrestamoInDB(**doc) async for doc in cursor]

async def count_prestamos_usuario(db: AsyncIOMotorDatabase, user_id: str, activos_only: bool = False) -> int:
    filtro = {"user_id": user_id}
    if activos_only:
        filtro["devuelto"] = False
    return await db["prestamos"].count_documents(filtro)

async def devolver_prestamo(db: AsyncIOMotorDatabase, prestamo_id: str):
    result = await db["prestamos"].update_one(
        {"_id": ObjectId(prestamo_id)},
        {"$set": {"devuelto": True, "fecha_real_devolucion": datetime.utcnow()}}
    )
    return result.modified_count
