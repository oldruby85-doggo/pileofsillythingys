Вариант A: GitHub — истина, Drive — зеркало для меня

Идея: ты работаешь локально, коммитишь и пушишь на GitHub, а в Google Drive держим автоматическую копию проекта (без .git, без .venv), чтобы я читала код через коннектор Drive.

Как сделать

Поставь Google Drive for Desktop. Выбери локальную папку, например:

C:\Users\Yahont\Google Drive\Projects\forbidden-castle\


Заведи скрипт синхронизации (PowerShell), положи в корень репо sync_to_drive.ps1:

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


После каждого пуша запускай:

pwsh -File .\sync_to_drive.ps1


или добавь в Git hook .git\hooks\post-commit:

#!/bin/sh
powershell -ExecutionPolicy Bypass -File sync_to_drive.ps1


В этом чате я открываю твои файлы через Drive. Ты пушишь — я читаю актуал.

Плюсы

Нормальный git-источник (GitHub), чистая история.

Drive даёт мне доступ без выкрутасов.

Минусы

Один доп. шаг (скрипт). Переживёшь.