FROM python:3.12

# Configuración básica
ENV PYTHONUNBUFFERED=1
WORKDIR /restaurant-ordering

# Instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código fuente
COPY . .