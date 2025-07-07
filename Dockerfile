FROM python:3.11-slim-bullseye

# Define o frontend do debian como não interativo para evitar prompts durante o build
ENV DEBIAN_FRONTEND=noninteractive

# Argumento para a versão do Chrome que você deseja instalar
# Deixe em branco para instalar a versão estável mais recente
ARG CHROME_VERSION=""

# Instala as dependências do sistema necessárias para o Selenium e o Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    unzip \
    jq \
    # Adiciona a chave GPG do Google (método recomendado para evitar `apt-key` obsoleto)
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    # Adiciona o repositório do Google Chrome
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    # Instala o Google Chrome
    && (if [ -n "$CHROME_VERSION" ]; then \
        apt-get install -y google-chrome-stable=${CHROME_VERSION}; \
    else \
        apt-get install -y google-chrome-stable; \
    fi) \
    # Instala o Chromedriver correspondente à versão estável para automação
    && CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url') \
    && wget -q ${CHROMEDRIVER_URL} -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    # Limpa o cache e arquivos temporários para reduzir o tamanho da imagem
    && rm -rf /var/lib/apt/lists/* /tmp/chromedriver.zip /tmp/chromedriver-linux64

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY . .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para o diretório de trabalho
COPY . .

# Comando para executar a sua aplicação
# Lembre-se de substituir 'seu_script.py' pelo nome do seu arquivo principal
CMD ["python", "DataColectorGF.py"]