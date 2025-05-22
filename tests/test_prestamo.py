# tests/test_prestamo.py
#import pytest
#from httpx import AsyncClient
#from app.main import app

#@pytest.mark.asyncio
#async def test_crear_prestamo_bad_request():
#    """
#    Enviar un JSON vacío debe devolver 422 o 400.
#    """
#    async with AsyncClient(app=app, base_url="http://test") as ac:
#        resp = await ac.post("/prestamos/", json={})
#    assert resp.status_code in (400, 422)

# Otros tests con payload correcto requieren mocking de MongoDB.
