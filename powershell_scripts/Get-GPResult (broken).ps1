# Define the output path for the HTML report
$OutputPath = "C:\Temp\GPResult.html"

# Ensure the output directory exists
if (!(Test-Path -Path (Split-Path -Path $OutputPath))) {
    New-Item -ItemType Directory -Path (Split-Path -Path $OutputPath) | Out-Null
}

# Run gpresult to generate a Group Policy result report in HTML format
gpresult /H $OutputPath /F

# Check if the file was created successfully
if (Test-Path $OutputPath) {
    # Read the HTML file and remove HTML tags to display plain text in the console
    $htmlContent = Get-Content -Path $OutputPath
    $plainText = $htmlContent -replace '<[^>]+>', '' -replace '&nbsp;', ' '

    # Output the plain text to the console
    Write-Output $plainText
} else {
    Write-Output "Failed to generate Group Policy report."
}
