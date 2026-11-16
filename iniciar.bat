@echo off
chcp 65001 > nul
title MapaLeads Pro - Prospecção no Google Maps
echo =======================================================
echo          MAPALEADS PRO - MINERADOR GOOGLE MAPS
echo   Mapeador de Negócios sem Site no Google Meu Negócio
echo =======================================================
echo.
echo [1/2] Verificando ambiente Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    pause
    exit /b
)

echo [2/2] Iniciando servidor local na porta 5055...
start "" "http://127.0.0.1:5055"
python server.py
pause
