# Dockerfile
FROM python:3.10-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia dependencias e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Expone el puerto de la app
EXPOSE 8000

# Variable de entorno para production (opcional)
ENV PYTHONUNBUFFERED=1

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
