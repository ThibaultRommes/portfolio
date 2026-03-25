# Création des cmdlet
# Considère le script comme un commande officielle (permet le WhatIf)
[CmdletBinding(SupportsShouldProcess=$true)]

param (
[Parameter(Mandatory=$true)]
[ValidateSet("Create", "Delete")]
[string]$Action,

[Parameter(Mandatory=$true)]
[string]$CsvPath
)


# Initialisation des variables (globales)
$UserPathRoot = "C:\UsersData"
$ArchivePath = "C:\Archives"
$LogPath = "C:\log"
$LogFile = "$LogPath\gestion_$(Get-Date -Format 'yyyyMMdd').log"


# Gestion des logs
function Write-Log {
    param([string]$Message, [string]$Type="INFO")
    
# 1. Création de la ligne de log horodatée
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$LogLine = "[$Timestamp] [$Type] $Message"
    
# 2. Écriture dans le fichier texte et affichage dans le shell
Add-Content -Path $LogFile -Value $LogLine
Write-Host $LogLine
}


# Gestion d’erreur CSV introuvable 
if (-not (Test-Path -Path $CsvPath)) {
    Write-Log "Erreur : Le fichier CSV '$CsvPath' est introuvable"
    return 
}

$CSV = Import-Csv -Path $CsvPath -Delimiter ";" -Encoding Default


foreach ($User in $CSV) {

# Initialisation des variables (dynamiques)
$CheminDossier = "$UserPathRoot\$($User.Login)"

# Actions pour la cmdlet Create
if ($Action -eq "Create") {

# 1. Vérification si le user n'existe pas on continue
# Gestion d'erreur utilisateur déjà existant
if (Get-ADUser -Filter "SamAccountName -eq '$($User.Login)'" -ErrorAction SilentlyContinue) {
Write-Log "Erreur : Le compte $($User.Login) existe deja, impossible de le creer"
}

else {
$UserTable = @{
SamAccountName = $User.Login
UserPrincipalName = "$($User.Login)@rt.local"
Name = "$($User.Prenom) $($User.Nom)"
GivenName = $User.Prenom
Surname = $User.Nom
Path = "OU=$($User.OU),DC=rt,DC=local"
AccountPassword = (ConvertTo-SecureString "Win2025!" -AsPlainText -Force)
ChangePasswordAtLogon = $true
Enabled = $true
}

# 2. Création des comptes users
New-ADUser @UserTable

# 3. Création du dossier personnel
New-Item -ItemType Directory -Path $CheminDossier -Force | Out-Null

# 4. Application et gestion des droits NTFS (via le module NTFSSecurity d’Active Directory)
Get-Item $CheminDossier | Disable-NTFSAccessInheritance
Add-NTFSAccess -Path $CheminDossier -Account "rt\$($User.Login)" -AccessRights FullControl

# 5. Log création user et dossier réussi
Write-Log "Utilisateur $($User.Login) et son dossier crees avec succes"
}
}


# Actions pour la cmdlet Delete
if ($Action -eq "Delete") {


# 1. Vérification si le user existe on continue
# Gestion d'erreur utilisateur introuvable
if (-not (Get-ADUser -Filter "SamAccountName -eq '$($User.Login)'" -ErrorAction SilentlyContinue)) {
Write-Log "Le compte $($User.Login) est introuvable, impossible de le supprimer"
}

else {
# 2. Suppression du compte Active Directory (via un CSV de suppression)
Remove-ADUser -Identity $User.Login -Confirm:$false


# 3. Automatisation du nom du fichier
$Date = Get-Date -Format "yyyyMMdd"
$ZipPath = "$ArchivePath\$($User.Login)_$Date.zip"

# 4. Compression en fichier ZIP dans le dossier des archives
Compress-Archive -Path $CheminDossier -DestinationPath $ZipPath -Force

# 5. Suppression du dossier original
Remove-Item -Path $CheminDossier -Recurse -Force

# 6. Log suppression et archivage réussi
Write-Log "Utilisateur $($User.Login) supprime et dossier archive avec succes"
}}
}