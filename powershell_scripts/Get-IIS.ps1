<#
.SYNOPSIS
Get-IIS.ps1 returns data about IIS installation.
.NOTES
Next line required by Kansa.ps1 to determine how output is treated.
OUTPUT TSV

Nod to Mike Fanning for concept
#>
$ErrorActionPreference = "SilentlyContinue"
$o = "" | Select-Object IISInstalled
if ((Get-ItemProperty HKLM:\Software\Microsoft\InetStp\Components\).W3SVC) {
    $o.IISInstalled = "True"
} else {
    $o.IISInstalled = "False"
}
$o