from bson import ObjectId, errors
from fastapi import HTTPException, status

from app.schemas.prestamo import PrestamoCreate, PrestamoInDB

async def create_prestamo(db, prestamo: PrestamoCreate) -> str:
    """
    Inserta un nuevo préstamo en la colección y retorna su ID como string.
    """
    data = prestamo.dict(by_alias=True)
    data.setdefault("devuelto", False)
    result = await db.prestamos.insert_one(data)
    return str(result.inserted_id)

async def get_prestamo(db, prestamo_id: str) -> PrestamoInDB | None:
    """
    Obtiene un único préstamo por su ID.
    """
    try:
        oid = ObjectId(prestamo_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de préstamo inválido: {prestamo_id}"
        )
    doc = await db.prestamos.find_one({"_id": oid})
    if not doc:
        return None
    return PrestamoInDB(**doc)

async def list_prestamos_usuario(
    db,
    user_id: str,
    activos_only: bool = False
) -> list[PrestamoInDB]:
    """
    Retorna una lista de préstamos para un usuario dado.

    - Si user_id == "*", no filtra por usuario.
    - Si activos_only es True, solo retorna aquellos con devuelto=False.
    """
    query: dict = {}
    if user_id and user_id != "*":
        query["user_id"] = user_id
    if activos_only:
        query["devuelto"] = False

    cursor = db.prestamos.find(query).sort("fecha_prestamo", -1)
    prestamos: list[PrestamoInDB] = []
    async for doc in cursor:
        prestamos.append(PrestamoInDB(**doc))
    return prestamos

async def count_prestamos_usuario(db, user_id: str) -> int:
    """
    Cuenta los préstamos activos (devuelto=False) de un usuario.
    """
    if not user_id:
        return 0
    return await db.prestamos.count_documents({
        "user_id": user_id,
        "devuelto": False
    })

async def devolver_prestamo(db, prestamo_id: str) -> bool:
    """
    Marca un préstamo como devuelto, si está activo.
    """
    try:
        oid = ObjectId(prestamo_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de préstamo inválido: {prestamo_id}"
        )

    result = await db.prestamos.update_one(
        {"_id": oid, "devuelto": False},
        {"$set": {"devuelto": True}}
    )
    return result.modified_count == 1
