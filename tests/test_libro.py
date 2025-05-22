# tests/test_libro.py
#import pytest
#from httpx import AsyncClient
#from app.main import app

#@pytest.mark.asyncio
#async def test_root():
#    async with AsyncClient(app=app, base_url="http://test") as ac:
#        resp = await ac.get("/")
#    assert resp.status_code == 200
#    assert resp.json() == {"message": "API de Biblioteca con MongoDB funcionando"}

#@pytest.mark.asyncio
#async def test_crear_leer_libro(tmp_path, monkeypatch):
#    """
#    Simula crear un libro y luego leerlo.
#    Necesita una setup de BD en memoria o mocking de Motor.
#    Aquí hacemos un ejemplo simple marcando 201.
#    """
#    payload = {
#        "titulo": "La Iliada",
#        "autor": "Homero",
#        "isbn": "1234567890123",
#        "paginas": 500
#    }
#    async with AsyncClient(app=app, base_url="http://test") as ac:
#        # Crear libro
#        create_resp = await ac.post("/libros/", json=payload)
#        assert create_resp.status_code == 201
#        data = create_resp.json()
#        assert data["titulo"] == payload["titulo"]
#        libro_id = data["id"]

        # Leer libro
#        read_resp = await ac.get(f"/libros/{libro_id}")
#        assert read_resp.status_code == 200
#        assert read_resp.json()["id"] == libro_id
