# app/routers/ui.py

from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db
from app.schemas.libro import LibroCreate, LibroOut
from app.schemas.prestamo import PrestamoCreate
from app.services.libro_service import (
    create_libro,
    get_libro,
    update_libro,
    delete_libro,
    list_libros
)
from app.services.prestamo_service import (
    create_prestamo,
    list_prestamos_usuario,
    devolver_prestamo,
    count_prestamos_usuario
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Página de Libros
@router.get("/ui/libros", response_class=HTMLResponse)
async def ui_libros(
    request: Request,
    isbn: str = Query("", description="Buscar por ISBN"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    libros = await list_libros(db, isbn_filter=isbn or None)
    return templates.TemplateResponse("libros.html", {
        "request": request,
        "libros": libros,
        "libro": {},
        "isbn": isbn
    })

@router.get("/ui/libros/edit/{id}", response_class=HTMLResponse)
async def ui_edit_libro(
    request: Request,
    id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    libro = await get_libro(db, id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libros = await list_libros(db)
    return templates.TemplateResponse("libros.html", {
        "request": request,
        "libros": libros,
        "libro": libro,
        "isbn": ""
    })

# Nuevo: Mostrar formulario de creación (GET) para evitar 422 en POST URL
@router.get("/ui/libros/save", response_class=HTMLResponse)
async def ui_create_libro_form(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    libros = await list_libros(db)
    return templates.TemplateResponse("libros.html", {
        "request": request,
        "libros": libros,
        "libro": {},
        "isbn": ""
    })

@router.post("/ui/libros/save")
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
        updated = await update_libro(db, id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Libro a actualizar no encontrado")
    else:
        await create_libro(db, data)
    return RedirectResponse(url=f"/ui/libros?isbn={isbn}", status_code=303)

@router.get("/ui/libros/delete/{id}")
async def ui_delete_libro(
    id: str,
    isbn: str = Query(""),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    deleted = await delete_libro(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Libro no encontrado para borrar")
    return RedirectResponse(url=f"/ui/libros?isbn={isbn}", status_code=303)

# Página de Préstamos
@router.get("/ui/prestamos", response_class=HTMLResponse)
async def ui_prestamos(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    params = request.query_params
    user_id = params.get("user_id") or params.get("user-id") or ""
    activos_only = params.get("activos_only", "false").lower() == "true"
    filtro = {"user_id": user_id, "activos_only": activos_only}
    prestamos = await list_prestamos_usuario(
        db,
        user_id=user_id or "*",
        activos_only=activos_only
    )
    return templates.TemplateResponse("prestamos.html", {
        "request": request,
        "prestamos": prestamos,
        "filtro": filtro
    })

@router.post("/ui/prestamos/save")
async def ui_save_prestamo(
    user_id: str = Form(...),
    libro_id: str = Form(...),
    fecha_prestamo: str = Form(...),
    fecha_devolucion: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    prestamos_activos = await count_prestamos_usuario(db, user_id)
    if prestamos_activos >= 5:
        raise HTTPException(status_code=400, detail="Usuario ha superado el límite de préstamos activos")
    await create_prestamo(db, PrestamoCreate(
        user_id=user_id,
        libro_id=libro_id,
        fecha_prestamo=fecha_prestamo + "Z",
        fecha_devolucion=fecha_devolucion + "Z"
    ))
    return RedirectResponse(url=f"/ui/prestamos?user_id={user_id}", status_code=303)

@router.get("/ui/prestamos/devolver/{id}")
async def ui_devolver(
    id: str,
    user_id: str = Query("", description="Usuario para filtro"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # Validamos que se recibió un ID
    if not id:
        raise HTTPException(status_code=404, detail="ID de préstamo inválido")

    success = await devolver_prestamo(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # Redirigimos de nuevo al listado, conservando el user_id
    return RedirectResponse(url=f"/ui/prestamos?user_id={user_id}", status_code=303)