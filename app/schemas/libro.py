from pydantic import BaseModel, Field

class LibroBase(BaseModel):
    titulo: str = Field(..., example="Cien años de soledad")
    autor: str  = Field(..., example="Gabriel García Márquez")
    isbn: str   = Field(..., min_length=10, max_length=13, example="1234567890123")
    paginas: int = Field(..., gt=0, example=432)

class LibroCreate(LibroBase):
    """
    Uso para creación: hereda todos los campos de LibroBase.
    """
    pass

class LibroOut(LibroBase):
    """
    Uso para respuestas: incluye el campo 'id' generado por MongoDB.
    """
    id: str = Field(..., example="60f5a3c8b4d1e25f8c8b4567")

    model_config = {
        # Pydantic v2: si usas atributos de un objeto, habilita from_attributes
        # aquí no es crítico porque pasamos dicts, pero evita la advertencia
        "from_attributes": True
    }
