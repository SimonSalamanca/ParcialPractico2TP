from sqlalchemy import Column, Integer, String
from app.core.database import Base

class LibroDB(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=False)
    paginas = Column(Integer, nullable=False)
