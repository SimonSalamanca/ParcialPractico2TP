from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import client
from app.routers.libro import router as libro_router
from app.routers.prestamo import router as prestamo_router
from app.routers.ui import router as ui_router

app = FastAPI(
    title="API Biblioteca",
    description="API de Gestión de Biblioteca usando FastAPI y MongoDB",
    version="1.0.0"
)

# Configurar plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_db_client():
    """
    Conecta con el cluster de MongoDB al iniciar la aplicación.
    """
    print("Conectando a MongoDB...")
    await client.admin.command("ping")
    print("MongoDB conectado")

@app.on_event("shutdown")
def shutdown_db_client():
    """
    Cierra la conexión con MongoDB al apagar la aplicación.
    """
    print("Cerrando conexión a MongoDB...")
    client.close()

# Incluir routers de los recursos y la UI
app.include_router(libro_router)
app.include_router(prestamo_router)
app.include_router(ui_router)

@app.get("/", tags=["root"])
async def read_root(request: Request):
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "API de Biblioteca con MongoDB funcionando"}
