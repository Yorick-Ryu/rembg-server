FROM python:3.13-slim

WORKDIR /app

RUN pip install rembg[cpu,cli] && \
    rembg d isnet-general-use

COPY . .

EXPOSE 7000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]