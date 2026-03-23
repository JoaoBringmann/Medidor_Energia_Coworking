FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc no disco e força o log a aparecer no terminal do Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema operacional necessárias para o PostgreSQL e MQTT
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte do projeto
COPY . .

# Prática de Segurança: Cria um usuário sem privilégios de root para rodar a aplicação
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expõe a porta que a API vai utilizar
EXPOSE 8000

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]