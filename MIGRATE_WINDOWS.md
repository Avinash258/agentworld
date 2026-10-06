# Migrated to C:\Project\aiAgentWorld

## Run (Windows)

### Backend (PowerShell)
```powershell
cd C:\Project\aiAgentWorld\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="."
uvicorn app.main:app --host 127.0.0.1 --port 8765
```

### Frontend (PowerShell)
```powershell
cd C:\Project\aiAgentWorld\frontend
npm install
npm run dev
```

Console: http://127.0.0.1:43123

### Skill import (Cursor on Windows)
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\skills\local-agentic-ai-platform"
Copy-Item -Recurse -Force C:\Project\aiAgentWorld\skills\local-agentic-ai-platform\* `
  "$env:USERPROFILE\.cursor\skills\local-agentic-ai-platform\"
```
