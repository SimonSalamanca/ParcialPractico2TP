from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

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

@app.get(
    "/", 
    response_class=HTMLResponse, 
    tags=["root"], 
    name="index"
)
async def index(request: Request):
    """
    Página de inicio: renderiza index.html
    """
    return templates.TemplateResponse("index.html", {"request": request})
if __name__ == "__main__":
    import uvicorn

    # Mostrar en consola las rutas disponibles
    print("==== RUTAS REGISTRADAS ====")
    for route in app.router.routes:
        # Solo imprimimos aquéllas que tengan nombre
        if getattr(route, "name", None):
            print(f"name={route.name:<30}  path={route.path}")
    print("============================")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
