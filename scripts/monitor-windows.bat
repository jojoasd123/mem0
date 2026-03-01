@echo off
REM Windows 11 进程监控脚本
REM 每5秒记录一次CPU和内存使用情况，自动轮转日志文件

set LOG_DIR=%USERPROFILE%\Desktop\monitor-logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 日志文件（带时间戳）
set LOG_FILE=%LOG_DIR%\win-resource-%date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%%time:~6,2%.log"
set LOG_FILE=%LOG_FILE: =0%

echo ======================================== >> "%LOG_FILE%"
echo 监控启动: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

REM 监控循环
:loop
set TIMESTAMP=%date% %time%

echo. >> "%LOG_FILE%"
echo [%TIMESTAMP%] --- Top 10 CPU --- >> "%LOG_FILE%"
wmic process get Name,ProcessId,PageFileUsage,WorkingSetSize /format:csv | findstr /V "Node,Name" | sort /R /+4 | head -n 11 >> "%LOG_FILE%" 2>&1

echo. >> "%LOG_FILE%"
echo [%TIMESTAMP%] --- Top 10 Memory --- >> "%LOG_FILE%"
wmic process get Name,ProcessId,PageFileUsage,WorkingSetSize /format:csv | findstr /V "Node,Name" | sort /R /+3 | head -n 11 >> "%LOG_FILE%" 2>&1

echo. >> "%LOG_FILE%"
echo [%TIMESTAMP%] --- CPU Load --- >> "%LOG_FILE%"
wmic cpu get LoadPercentage /value >> "%LOG_FILE%" 2>&1

echo ======================================== >> "%LOG_FILE%"

timeout /t 5 /nobreak > nul
goto loop
