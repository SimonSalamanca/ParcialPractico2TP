from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db
from app.schemas.libro import LibroCreate
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
        "request": request, "libros": libros, "libro": {}, "isbn": isbn
    })

@router.get("/ui/libros/edit/{id}", response_class=HTMLResponse)
async def ui_edit_libro(request: Request, id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    libro = await get_libro(db, id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libros = await list_libros(db)
    return templates.TemplateResponse("libros.html", {
        "request": request, "libros": libros, "libro": libro
    })

@router.post("/ui/libros/save")
async def ui_save_libro(
    user_id: str = Form(...),
    libro_id: str = Form(...),
    fecha_prestamo: str = Form(...),
    fecha_devolucion: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        await create_prestamo(db, PrestamoCreate(
            user_id=user_id,
            libro_id=libro_id,
            fecha_prestamo=fecha_prestamo + "Z",
            fecha_devolucion=fecha_devolucion + "Z"
        ))
        return RedirectResponse(url=f"/ui/prestamos?user_id={user_id}", status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = LibroCreate(titulo=titulo, autor=autor, isbn=isbn, paginas=paginas)
    if id:
        updated = await update_libro(db, id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Libro a actualizar no encontrado")
        return RedirectResponse(url="/ui/libros", status_code=303)
    else:
        await create_libro(db, data)
        return JSONResponse(content={"message": "Libro creado exitosamente"}, status_code=201)

@router.get("/ui/libros/delete/{id}")
async def ui_delete_libro(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    deleted = await delete_libro(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Libro no encontrado para borrar")
    return RedirectResponse(url="/ui/libros", status_code=303)

# Página de Préstamos
@router.get("/ui/prestamos", response_class=HTMLResponse)
async def ui_prestamos(
    request: Request,
    user_id: str = Query("", description="Filtrar por usuario"),
    activos_only: bool = Query(False, description="Solo préstamos activos"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
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
    return JSONResponse(content={"message": "Préstamo creado exitosamente"}, status_code=201)

@router.get("/ui/prestamos/devolver/{id}")
async def ui_devolver(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    success = await devolver_prestamo(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return RedirectResponse(url="/ui/prestamos", status_code=303)
