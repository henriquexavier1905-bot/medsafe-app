FROM python:3-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# O Render define a porta via variável de ambiente $PORT; repassamos
# isso pro Flet através de FLET_SERVER_PORT (com 8000 como padrão local).
CMD ["/bin/sh", "-c", "FLET_SERVER_PORT=${PORT:-8000} python main.py"]
