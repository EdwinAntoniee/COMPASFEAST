FROM python:3.12-slim

WORKDIR /app

COPY BackEnd/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY BackEnd ./BackEnd
COPY FrontEnd ./FrontEnd

WORKDIR /app/BackEnd

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
