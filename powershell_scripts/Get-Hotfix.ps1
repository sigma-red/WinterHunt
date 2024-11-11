<#
.SYNOPSIS
Get-Hotfix.ps1 returns data about installed hotfixes.
.NOTES
The next line is needed by Kansa.ps1 to determine how to handle output
from this script.
OUTPUT TSV

Contributed by Mike Fanning
#>
Get-HotFix | Select-Object HotfixID, Caption, Description, InstalledBy