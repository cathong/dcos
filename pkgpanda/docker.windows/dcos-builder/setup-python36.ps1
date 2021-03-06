$ErrorActionPreference = "stop"

$pip_url = 'https://bootstrap.pypa.io/get-pip.py'
$python_url = 'https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe'
$pythonDownloadPath = Join-Path $env:TEMP "python-3.6.8-amd64.exe"
$pipDownloadPath = Join-Path $env:TEMP "get-pip.py"
$pythonInstallDir = Join-Path $env:SystemDrive "Python36"
$INSTALL_ARGS = @("/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=$pythonInstallDir")

Write-Output "Downloading $python_url"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $python_url -OutFile $pythonDownloadPath -MaximumRetryCount 5 -RetryIntervalSec 5

If(!(test-path $pythonInstallDir))
{
      New-Item -ItemType Directory -Force -Path $pythonInstallDir
}

$parameters = @{
'FilePath' = $pythonDownloadPath
'ArgumentList' = $INSTALL_ARGS
'Wait' = $true
'PassThru' = $true
}

$p = Start-Process @parameters
if($p.ExitCode -ne 0) {
    Throw "Failed to install $pythonDownloadPath"
}

[Environment]::SetEnvironmentVariable("PATH", "${env:path};${pythonInstallDir}\Scripts", "Machine") 

Write-Output "Downloading $pip_url"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $pip_url -OutFile $pipDownloadPath -MaximumRetryCount 5 -RetryIntervalSec 5

& $pythonInstallDir\python.exe $pipDownloadPath --no-warn-script-location

Remove-Item -Path $pythonDownloadPath
Remove-Item -Path $pipDownloadPath
