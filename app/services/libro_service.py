from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.libro import LibroCreate, LibroOut
from bson import ObjectId

async def create_libro(db: AsyncIOMotorDatabase, libro: LibroCreate) -> LibroOut:
    result = await db['libros'].insert_one(libro.dict())
    doc = await db['libros'].find_one({'_id': result.inserted_id})
    doc['id'] = str(doc['_id'])
    return LibroOut(**doc)

async def get_libro(db: AsyncIOMotorDatabase, id: str) -> Optional[LibroOut]:
    doc = await db['libros'].find_one({'_id': ObjectId(id)})
    if doc:
        doc['id'] = str(doc['_id'])
        return LibroOut(**doc)
    return None

async def update_libro(db: AsyncIOMotorDatabase, id: str, libro: LibroCreate) -> Optional[LibroOut]:
    result = await db['libros'].update_one({'_id': ObjectId(id)}, {'$set': libro.dict()})
    if result.modified_count:
        doc = await db['libros'].find_one({'_id': ObjectId(id)})
        doc['id'] = str(doc['_id'])
        return LibroOut(**doc)
    return None

async def delete_libro(db: AsyncIOMotorDatabase, id: str) -> bool:
    result = await db['libros'].delete_one({'_id': ObjectId(id)})
    return result.deleted_count == 1

async def list_libros(
    db: AsyncIOMotorDatabase,
    isbn_filter: Optional[str] = None
) -> List[LibroOut]:
    """
    Recupera libros de la colección 'libros'. Si isbn_filter se proporciona,
    solo devuelve aquellos con ISBN igual a isbn_filter.
    """
    resultados: List[LibroOut] = []
    query = {}
    if isbn_filter:
        query['isbn'] = isbn_filter

    cursor = db['libros'].find(query)
    async for doc in cursor:
        doc['id'] = str(doc['_id'])
        resultados.append(LibroOut(**doc))
    return resultados
