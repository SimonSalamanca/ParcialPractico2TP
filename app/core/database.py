# app/core/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config     import settings

# Antes:
# client = AsyncIOMotorClient(settings.mongodb_url)

# Después:
client = AsyncIOMotorClient(str(settings.mongodb_url))
db     = client[settings.mongodb_db]

async def get_db():
    """
    Dependencia de FastAPI que inyecta la base de datos MongoDB.
    """
    try:
        yield db
    finally:
        pass
