from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.prestamo import PrestamoCreate, PrestamoOut
from app.models.prestamo import PrestamoInDB
from bson import ObjectId
from datetime import datetime

MAX_PRESTAMOS_ACTIVOS = 3

async def create_prestamo(db: AsyncIOMotorDatabase, prestamo: PrestamoCreate) -> PrestamoOut:
    # Verificar si el usuario ya tiene el máximo de préstamos activos
    activos = await count_prestamos_usuario(db, prestamo.user_id, activos_only=True)
    if activos >= MAX_PRESTAMOS_ACTIVOS:
        raise ValueError("El usuario ha alcanzado el número máximo de préstamos activos.")

    prestamo_dict = prestamo.dict()
    prestamo_dict["devuelto"] = False
    result = await db["prestamos"].insert_one(prestamo_dict)
    doc = await db["prestamos"].find_one({"_id": result.inserted_id})
    doc["id"] = str(doc["_id"])
    return PrestamoOut(**doc)

async def list_prestamos_usuario(db: AsyncIOMotorDatabase, user_id: str, activos_only: bool = False) -> list[PrestamoInDB]:
    filtro: dict = {}
    if user_id and user_id != "*":
        filtro["user_id"] = user_id
    if activos_only:
        filtro["devuelto"] = False

    cursor = db["prestamos"].find(filtro)
    resultados: list[PrestamoInDB] = []
    async for doc in cursor:
        # 1) Convertimos ObjectId a string
        doc["id"] = str(doc["_id"])
        # 2) Eliminamos el campo _id para no pasarlo al modelo
        doc.pop("_id", None)
        resultados.append(PrestamoInDB(**doc))
    return resultados

async def count_prestamos_usuario(db: AsyncIOMotorDatabase, user_id: str, activos_only: bool = False) -> int:
    # Si user_id está vacío o es comodín, no cuenta
    if not user_id or user_id == "*":
        return 0
    filtro: dict = {"user_id": user_id}
    if activos_only:
        filtro["devuelto"] = False
    return await db["prestamos"].count_documents(filtro)

async def devolver_prestamo(db: AsyncIOMotorDatabase, prestamo_id: str) -> bool:
    result = await db["prestamos"].update_one(
        {"_id": ObjectId(prestamo_id), "devuelto": False},
        {"$set": {"devuelto": True, "fecha_real_devolucion": datetime.utcnow()}}
    )
    return result.modified_count == 1

async def get_prestamo(db: AsyncIOMotorDatabase, prestamo_id: str) -> PrestamoOut | None:
    """
    Recupera un préstamo por su ID.
    """
    doc = await db["prestamos"].find_one({"_id": ObjectId(prestamo_id)})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return PrestamoOut(**doc)
