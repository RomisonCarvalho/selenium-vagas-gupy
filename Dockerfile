# Imagem base enxuta com Python 3.12.
# A versão 3.12 mantém compatibilidade com as dependências utilizadas no projeto.
FROM python:3.12-slim

# Define /app como diretório de trabalho dentro do container.
# Os comandos seguintes passam a ser executados a partir desse diretório.
WORKDIR /app

# Instala o Chromium e o ChromeDriver fornecidos pela distribuição Linux.
# O ChromeDriver permite que o Selenium controle o navegador dentro do container.
# Ao final, remove o cache do apt para reduzir o tamanho da imagem.
RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# Copia primeiro somente o arquivo de dependências.
# Essa ordem permite reaproveitar o cache do Docker quando apenas o código Python muda.
COPY requirements.txt .

# Instala as dependências Python sem manter o cache local do pip na imagem.
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos permitidos pelo .dockerignore para /app.
COPY . .

# Comando executado quando o container é iniciado.
# No Cloud Run Job, o container encerra quando o script termina.
CMD ["python", "projeto_vagas_gupy.py"]
