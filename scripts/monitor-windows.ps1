# Windows 11 进程监控 PowerShell 脚本
# 每5秒记录一次CPU和内存使用情况

$LogDir = "$env:USERPROFILE\Desktop\monitor-logs"
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = "$LogDir\win-resource-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$MaxLogSize = 10MB

Write-Output "========================================" | Tee-Object -FilePath $LogFile
Write-Output "监控启动: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $LogFile -Append
Write-Output "========================================" | Tee-Object -FilePath $LogFile -Append

# 监控循环
while ($true) {
    $Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    
    # 检查日志文件大小，超过则轮换
    if ((Get-Item $LogFile -ErrorAction SilentlyContinue).Length -gt $MaxLogSize) {
        $LogFile = "$LogDir\win-resource-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
        Write-Output "========================================" | Tee-Object -FilePath $LogFile
        Write-Output "日志轮换: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $LogFile -Append
    }
    
    Write-Output "" | Tee-Object -FilePath $LogFile -Append
    Write-Output "[$Timestamp] --- Top 10 CPU ---" | Tee-Object -FilePath $LogFile -Append
    Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table -AutoSize | Out-String -Width 4096 | Tee-Object -FilePath $LogFile -Append
    
    Write-Output "" | Tee-Object -FilePath $LogFile -Append
    Write-Output "[$Timestamp] --- Top 10 Memory ---" | Tee-Object -FilePath $LogFile -Append
    Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 | Format-Table -AutoSize | Out-String -Width 4096 | Tee-Object -FilePath $LogFile -Append
    
    Write-Output "" | Tee-Object -FilePath $LogFile -Append
    Write-Output "[$Timestamp] --- CPU Load ---" | Tee-Object -FilePath $LogFile -Append
    $cpuLoad = (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    Write-Output "CPU 总使用率: $cpuLoad%" | Tee-Object -FilePath $LogFile -Append
    
    Write-Output "========================================" | Tee-Object -FilePath $LogFile -Append
    
    Start-Sleep -Seconds 5
}
