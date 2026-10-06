# Run in PowerShell on your Windows machine
$dest = "C:\Project\aiAgentWorld"
New-Item -ItemType Directory -Force -Path "C:\Project" | Out-Null

# If you downloaded aiAgentWorld.zip from the agent artifacts:
# $zip = "$env:USERPROFILE\Downloads\aiAgentWorld.zip"
# Expand-Archive -Path $zip -DestinationPath "C:\Project" -Force

# Preferred: clone from Origin via WSL, then the folder is on Windows at C:\Project\aiAgentWorld
Write-Host "Preferred path: use WSL commands in MIGRATE_WINDOWS / agent instructions."
Write-Host "Destination: $dest"
