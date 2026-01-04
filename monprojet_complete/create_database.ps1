# Script PowerShell pour créer la base de données MySQL
# Utilisation: .\create_database.ps1

Write-Host "Script de création de la base de données MySQL" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Demander les informations de connexion MySQL
$dbUser = Read-Host "Nom d'utilisateur MySQL (par défaut: root)"
if ([string]::IsNullOrWhiteSpace($dbUser)) {
    $dbUser = "root"
}

$dbPassword = Read-Host "Mot de passe MySQL" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

Write-Host ""
Write-Host "Tentative de connexion à MySQL..." -ForegroundColor Yellow

# Créer un fichier SQL temporaire
$sqlFile = "temp_create_db.sql"
$sqlContent = "CREATE DATABASE IF NOT EXISTS research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
$sqlContent | Out-File -FilePath $sqlFile -Encoding UTF8

# Essayer d'exécuter la commande MySQL
$mysqlPath = "mysql"
$mysqlFound = $false

# Chercher MySQL dans les chemins communs
$commonPaths = @(
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
    "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe",
    "C:\xampp\mysql\bin\mysql.exe",
    "C:\wamp\bin\mysql\mysql8.0.27\bin\mysql.exe"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        $mysqlPath = $path
        $mysqlFound = $true
        Write-Host "MySQL trouvé à: $path" -ForegroundColor Green
        break
    }
}

# Vérifier si MySQL est dans le PATH
if (-not $mysqlFound) {
    try {
        $null = Get-Command mysql -ErrorAction Stop
        $mysqlFound = $true
        Write-Host "MySQL trouvé dans le PATH" -ForegroundColor Green
    } catch {
        $mysqlFound = $false
    }
}

if (-not $mysqlFound) {
    Write-Host ""
    Write-Host "ERREUR: MySQL n'a pas été trouvé dans les chemins standard." -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "1. Créez la base de données manuellement avec MySQL Workbench ou phpMyAdmin" -ForegroundColor White
    Write-Host "2. Ajoutez MySQL au PATH et réessayez" -ForegroundColor White
    Write-Host "3. Exécutez manuellement dans MySQL:" -ForegroundColor White
    Write-Host "   CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor Cyan
    Write-Host ""
    
    # Afficher le contenu du fichier SQL
    Write-Host "Le fichier SQL a été créé: $sqlFile" -ForegroundColor Yellow
    Write-Host "Vous pouvez l'exécuter manuellement avec:" -ForegroundColor Yellow
    Write-Host "  mysql -u $dbUser -p < $sqlFile" -ForegroundColor Cyan
    
    Remove-Item $sqlFile -ErrorAction SilentlyContinue
    exit 1
}

# Construire la commande MySQL
$mysqlCommand = "$mysqlPath -u $dbUser -p`"$dbPasswordPlain`" -e `"CREATE DATABASE IF NOT EXISTS research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`""

try {
    Write-Host "Création de la base de données..." -ForegroundColor Yellow
    Invoke-Expression $mysqlCommand 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCÈS: La base de données 'research_platform' a été créée!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Prochaines étapes:" -ForegroundColor Cyan
        Write-Host "1. Vérifiez que votre fichier .env contient les bonnes informations" -ForegroundColor White
        Write-Host "2. Exécutez: python manage.py migrate" -ForegroundColor Yellow
        Write-Host "3. Exécutez: python manage.py createsuperuser" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "ERREUR lors de la création de la base de données." -ForegroundColor Red
        Write-Host "Vérifiez vos identifiants MySQL et réessayez." -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Essayez de créer la base de données manuellement:" -ForegroundColor Yellow
    Write-Host "  mysql -u $dbUser -p" -ForegroundColor Cyan
    Write-Host "  CREATE DATABASE research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor Cyan
}

# Nettoyer
Remove-Item $sqlFile -ErrorAction SilentlyContinue

Write-Host ""

