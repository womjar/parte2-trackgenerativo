FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copiar código y tests
COPY app ./app
COPY tests ./tests

# Asegurar que /app esté en el PYTHONPATH
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
