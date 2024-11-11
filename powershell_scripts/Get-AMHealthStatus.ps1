<#
.SYNOPSIS
Get-AMHealthStatus.ps1 interogates WMI for AntimalwareHealthStatus
.NOTES
Contributed by Mike Fanning
#>
Get-WmiObject -namespace root\Microsoft\SecurityClient -Class AntimalwareHealthStatus