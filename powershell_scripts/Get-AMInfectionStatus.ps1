<#
.SYNOPSIS
Get-AMInfectionStatus.ps1 returns data about MS' Anti-Malware engine
relating to infections.

.NOTES
# Contributed by Mike Fanning
#>
Get-WmiObject -Namespace root\Microsoft\SecurityClient -Class AntimalwareInfectionStatus