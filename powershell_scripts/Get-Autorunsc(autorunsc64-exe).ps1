# Define the path to autorunsc.exe
$autorunscPath = "C:\Tools\autorunsc64.exe"  # Update this path to the actual location of autorunsc.exe

# Check if autorunsc.exe exists at the specified path
if (!(Test-Path -Path $autorunscPath)) {
    Write-Output "Error: autorunsc64.exe not found at $autorunscPath"
    return
}

# Run autorunsc.exe with the desired parameters
try {
    $output = & $autorunscPath /accepteula /nobanner
    Write-Output $output
} catch {
    Write-Output "Error running autorunsc64.exe: $_"
}