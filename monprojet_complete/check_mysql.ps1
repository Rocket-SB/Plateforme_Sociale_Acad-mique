# Script pour vérifier la connexion MySQL et lister les bases de données

Write-Host "Vérification de la connexion MySQL" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Demander les informations
$dbUser = Read-Host "Nom d'utilisateur MySQL (par défaut: root)"
if ([string]::IsNullOrWhiteSpace($dbUser)) {
    $dbUser = "root"
}

$dbPassword = Read-Host "Mot de passe MySQL" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

Write-Host ""
Write-Host "Test de connexion..." -ForegroundColor Yellow

# Chercher MySQL
$mysqlPath = "mysql"
$mysqlFound = $false

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
        break
    }
}

if (-not $mysqlFound) {
    try {
        $null = Get-Command mysql -ErrorAction Stop
        $mysqlFound = $true
    } catch {
        Write-Host "ERREUR: MySQL n'est pas trouvé. Vérifiez l'installation." -ForegroundColor Red
        exit 1
    }
}

# Lister les bases de données
Write-Host "Bases de données existantes:" -ForegroundColor Green
$command = "$mysqlPath -u $dbUser -p`"$dbPasswordPlain`" -e `"SHOW DATABASES;`""
Invoke-Expression $command

Write-Host ""
Write-Host "Vérification de 'research_platform'..." -ForegroundColor Yellow
$checkCommand = "$mysqlPath -u $dbUser -p`"$dbPasswordPlain`" -e `"SHOW DATABASES LIKE 'research_platform';`""
$result = Invoke-Expression $checkCommand

if ($result -match "research_platform") {
    Write-Host "✓ La base de données 'research_platform' existe!" -ForegroundColor Green
} else {
    Write-Host "✗ La base de données 'research_platform' n'existe pas." -ForegroundColor Red
    Write-Host ""
    Write-Host "Pour la créer, exécutez:" -ForegroundColor Yellow
    Write-Host "  .\create_database.ps1" -ForegroundColor Cyan
}

Write-Host ""

