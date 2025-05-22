
# File: app/services/prestamo_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Union

from app.schemas.prestamo import PrestamoCreate, PrestamoInDB, PrestamoOut

async def create_prestamo(db: AsyncIOMotorDatabase, prestamo: PrestamoCreate) -> dict:
    data = prestamo.model_dump()
    data['fecha_real_devolucion'] = None
    data['devuelto'] = False
    result = await db.prestamos.insert_one(data)
    return await get_prestamo(db, str(result.inserted_id))

async def get_prestamo(db: AsyncIOMotorDatabase, id: str) -> Union[PrestamoOut, None]:
    doc = await db.prestamos.find_one({'_id': ObjectId(id)})
    if not doc:
        return None
    # Convert ObjectId to str for id field
    doc['_id'] = str(doc['_id'])
    return PrestamoOut(**doc)

async def list_prestamos_usuario(
    db: AsyncIOMotorDatabase,
    user_id: str,
    activos_only: bool = False
) -> List[dict]:
    # Build query
    query = {} if user_id == '*' else {'user_id': user_id}
    if activos_only:
        query['devuelto'] = False
    # Fetch raw documents
    docs = await db.prestamos.find(query).to_list(length=None)
    # Convert ObjectId to str
    for doc in docs:
        doc['_id'] = str(doc['_id'])
    return docs

async def devolver_prestamo(db: AsyncIOMotorDatabase, id: str) -> Union[PrestamoOut, None]:
    # Mark as returned
    update = {
        '$set': {'devuelto': True, 'fecha_real_devolucion': datetime.utcnow()}
    }
    result = await db.prestamos.find_one_and_update(
        {'_id': ObjectId(id), 'devuelto': False},
        update,
        return_document=True
    )
    if not result:
        return None
    # Convert ObjectId to str
    result['_id'] = str(result['_id'])
    return PrestamoOut(**result)

