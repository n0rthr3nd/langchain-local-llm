# Script de configuracion para Windows PowerShell
# Ejecutar como: .\scripts\setup.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " LangChain + Ollama: Setup para Windows" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Verificar Docker Desktop
Write-Host "`n[1/5] Verificando Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $?) {
    Write-Host "ERROR: Docker Desktop no esta corriendo." -ForegroundColor Red
    Write-Host "Por favor, inicia Docker Desktop y vuelve a ejecutar este script." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Docker Desktop esta corriendo." -ForegroundColor Green

# Crear red de Docker
Write-Host "`n[2/5] Configurando red Docker..." -ForegroundColor Yellow
docker network create langchain-net 2>$null
Write-Host "OK: Red configurada." -ForegroundColor Green

# Iniciar servicios
Write-Host "`n[3/5] Iniciando contenedores..." -ForegroundColor Yellow
docker-compose up -d ollama
Write-Host "OK: Ollama iniciado." -ForegroundColor Green

# Esperar a que Ollama este listo
Write-Host "`n[4/5] Esperando a que Ollama este listo..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
do {
    Start-Sleep -Seconds 2
    $attempt++
    $health = docker exec ollama-server curl -s http://localhost:11434/api/tags 2>$null
} while (-not $health -and $attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host "ERROR: Ollama no responde despues de 60 segundos." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Ollama esta listo." -ForegroundColor Green

# Descargar modelo
Write-Host "`n[5/5] Descargando modelo llama3.2..." -ForegroundColor Yellow
Write-Host "Esto puede tardar varios minutos dependiendo de tu conexion..." -ForegroundColor Gray
docker exec ollama-server ollama pull llama3.2

# Descargar modelo de embeddings para RAG
Write-Host "`nDescargando modelo de embeddings (nomic-embed-text)..." -ForegroundColor Yellow
docker exec ollama-server ollama pull nomic-embed-text

Write-Host "`n================================================" -ForegroundColor Green
Write-Host " Setup completado exitosamente!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "`nPara iniciar la aplicacion LangChain:"
Write-Host "  docker-compose up -d" -ForegroundColor Cyan
Write-Host "`nPara ver los logs:"
Write-Host "  docker-compose logs -f" -ForegroundColor Cyan
Write-Host "`nPara ejecutar ejemplos manualmente:"
Write-Host "  docker exec -it langchain-app python main.py" -ForegroundColor Cyan
Write-Host "`nAPI disponible en: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Documentacion API: http://localhost:8000/docs" -ForegroundColor Yellow
