# ---- build/runtime base ----
FROM python:3.12-slim AS base

# Evita pyc, garante logging imediato
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instala dependências do sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Cria user não-root
RUN useradd -m appuser
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o código
COPY . .

# Troca para usuário não-root
USER appuser

# Exponha a porta do uvicorn
EXPOSE 8000

# Healthcheck simples (opcional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

# Comando de inicialização (produção)
# Workers: 1 (CPU-bound não é o caso; pode subir para 2-4 se quiser)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
