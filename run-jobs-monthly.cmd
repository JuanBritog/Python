@echo off
setlocal enabledelayedexpansion

REM Configuración del ambiente
set "PYTHON_PATH=C:\Program Files\Python312\python.exe"
set "SCRIPT_PATH=D:\SPA\Python\esecutore-jobs.py"
set "LOG_PATH=D:\SPA\Python\schedulatore_multi_script.log"
set "CMD_LOG_PATH=D:\SPA\Python\cmd_execution_monthly.log"

REM Inicialización de variables
set "RETURN_CODE=1"
set "job_eseguiti=0"
set "errori_trovati=0"

REM Inicio del log
echo Inizio esecuzione monthly jobs: %date% %time% > "%CMD_LOG_PATH%"

REM Ejecución del script Python con parámetro 2 (monthly)
"%PYTHON_PATH%" "%SCRIPT_PATH%" 2 >> "%CMD_LOG_PATH%" 2>&1

REM Verificación de la existencia del archivo de log
if not exist "%LOG_PATH%" (
    echo Errore: File di log non trovato. >> "%CMD_LOG_PATH%"
    set "RETURN_CODE=1"
    goto fine
)

REM Análisis del archivo de log
for /f "tokens=*" %%a in ('type "%LOG_PATH%"') do (
    echo %%a | findstr /i "error errore failed" > nul
    if !errorlevel! equ 0 (
        set /a "errori_trovati+=1"
    ) else (
        echo %%a | findstr /C:"eseguito con successo" > nul
        if !errorlevel! equ 0 (
            set /a "job_eseguiti+=1"
        )
    )
)

REM Determinación del RETURN_CODE
if %errori_trovati% gtr 0 (
    set "RETURN_CODE=1"
) else (
    set "RETURN_CODE=0"
)

:fine
REM Visualización de resultados
echo RETURN_CODE:%RETURN_CODE% jobs:%job_eseguiti% errori:%errori_trovati% >> "%CMD_LOG_PATH%"
echo Fine esecuzione monthly jobs: %date% %time% >> "%CMD_LOG_PATH%"

REM Muestra el resultado en la consola
type "%CMD_LOG_PATH%"

REM Salida con el RETURN_CODE apropiado
exit /b %RETURN_CODE%