from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db
from app.services.prestamo_service import list_prestamos_usuario, devolver_prestamo
from app.services.prestamo_service import create_prestamo
from app.services.libro_service import (
    create_libro,
    get_libro,
    update_libro,
    delete_libro,
    list_libros
)
from app.schemas.prestamo import PrestamoCreate
from app.schemas.libro import LibroCreate

# Definimos un router con prefijo para todas las rutas de UI
router = APIRouter(
    prefix="/ui",
    tags=["ui"],
    responses={404: {"description": "Not found"}}
)

# Configuración de plantillas
templates = Jinja2Templates(directory="templates")

# Página de Libros con búsqueda por ISBN
@router.get("/libros", response_class=HTMLResponse)
async def ui_libros(
    request: Request,
    isbn: str = Query("", description="Buscar por ISBN"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    libros = await list_libros(db, isbn_filter=isbn or None)
    filtro = {"isbn": isbn}
    return templates.TemplateResponse("libros.html", {
        "request": request,
        "libros": libros,
        "libro": {},
        "filtro": filtro
    })

@router.get("/libros/edit/{id}", response_class=HTMLResponse)
async def ui_edit_libro(
    request: Request,
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    libro = await get_libro(db, id)
    libros = await list_libros(db)
    return templates.TemplateResponse("libros.html", {
        "request": request,
        "libros": libros,
        "libro": libro,
        "filtro": {"isbn": ""}
    })

@router.post("/libros/save")
async def ui_save_libro(
    id: str = Form(""),
    titulo: str = Form(...),
    autor: str = Form(...),
    isbn: str = Form(...),
    paginas: int = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = LibroCreate(titulo=titulo, autor=autor, isbn=isbn, paginas=paginas)
    if id:
        await update_libro(db, id, data)
    else:
        await create_libro(db, data)
    return RedirectResponse(url=f"/ui/libros?isbn={isbn}", status_code=303)

@router.get("/libros/delete/{id}")
async def ui_delete_libro(
    id: str,
    isbn: str = Query(""),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    await delete_libro(db, id)
    return RedirectResponse(url=f"/ui/libros?isbn={isbn}", status_code=303)

# Página de Préstamos
@router.get("/prestamos", response_class=HTMLResponse)
async def ui_prestamos(
    request: Request,
    user_id: str = Query("", description="Filtrar por usuario"),
    activos_only: bool = Query(False, description="Solo préstamos activos"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    raw_docs = await list_prestamos_usuario(
        db,
        user_id=user_id or "*",
        activos_only=activos_only
    )
    prestamos = []
    for d in raw_docs:
        d["_id"] = str(d["_id"])
        d["id"] = d["_id"]
        prestamos.append(d)

    return templates.TemplateResponse("prestamos.html", {
        "request": request,
        "prestamos": prestamos,
        "filtro": {"user_id": user_id, "activos_only": activos_only}
    })

@router.post("/prestamos/save")
async def ui_save_prestamo(
    user_id: str = Form(...),
    libro_id: str = Form(...),
    fecha_prestamo: str = Form(...),
    fecha_devolucion: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await create_prestamo(db, PrestamoCreate(
        user_id=user_id,
        libro_id=libro_id,
        fecha_prestamo=fecha_prestamo + "Z",
        fecha_devolucion=fecha_devolucion + "Z"
    ))
    return RedirectResponse(url=f"/ui/prestamos?user_id={user_id}", status_code=303)

@router.get("/prestamos/devolver/{id}")
async def ui_devolver(
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    await devolver_prestamo(db, id)
    return RedirectResponse(url="/ui/prestamos", status_code=303)
