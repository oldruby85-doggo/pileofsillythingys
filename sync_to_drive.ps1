param(
  [string]$Dst = "$env:USERPROFILE\Google Drive\Projects\forbidden-castle"
)

$Src = (Get-Location).Path

# создаём папку-назначение
New-Item -ItemType Directory -Force -Path $Dst | Out-Null

# Копируем всё, зеркалим, но исключаем мусор и приватное
robocopy "$Src" "$Dst" /MIR /NFL /NDL /NP /R:1 /W:1 `
  /XD ".git" ".venv" "__pycache__" "dist" "build" ".idea" ".vscode" `
  /XF "*.pyc" "*.bak"
