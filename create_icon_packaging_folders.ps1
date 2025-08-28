$iconDir = "d:\web_proyects\imprenta_gallito\static\media\product_images\icons_packaging"

Get-ChildItem -Path $iconDir -Filter *.png | ForEach-Object {
    $folderName = $_.BaseName
    $folderPath = Join-Path $iconDir $folderName
    if (-not (Test-Path $folderPath)) {
        New-Item -Path $folderPath -ItemType Directory | Out-Null
    }
}
