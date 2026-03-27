param(
    [string]$InputDir = "D:\Projects\Orynd\info",
    [string]$OutputDir = "D:\Projects\Orynd\info\ocr"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Runtime.WindowsRuntime

$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]

function Await-AsyncOperation {
    param(
        [Parameter(Mandatory = $true)]$Operation,
        [Parameter(Mandatory = $true)][Type]$ResultType
    )

    $method = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object {
            $_.Name -eq "AsTask" -and
            $_.IsGenericMethod -and
            $_.GetParameters().Count -eq 1
        } |
        Select-Object -First 1

    $genericMethod = $method.MakeGenericMethod($ResultType)
    $task = $genericMethod.Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}

function Await-AsyncAction {
    param(
        [Parameter(Mandatory = $true)]$Action
    )

    $method = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object {
            $_.Name -eq "AsTask" -and
            -not $_.IsGenericMethod -and
            $_.GetParameters().Count -eq 1
        } |
        Select-Object -First 1

    $task = $method.Invoke($null, @($Action))
    $task.Wait()
}

function Get-OcrTextForPdf {
    param(
        [Parameter(Mandatory = $true)][string]$PdfPath
    )

    $file = Await-AsyncOperation `
        -Operation ([Windows.Storage.StorageFile]::GetFileFromPathAsync($PdfPath)) `
        -ResultType ([Windows.Storage.StorageFile])
    $document = Await-AsyncOperation `
        -Operation ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) `
        -ResultType ([Windows.Data.Pdf.PdfDocument])
    $ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()

    if ($null -eq $ocrEngine) {
        throw "Windows OCR engine is unavailable for the current user profile."
    }

    $parts = New-Object System.Collections.Generic.List[string]

    for ($pageIndex = 0; $pageIndex -lt $document.PageCount; $pageIndex++) {
        $page = $document.GetPage($pageIndex)
        try {
            $stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
            Await-AsyncAction -Action ($page.RenderToStreamAsync($stream))
            $stream.Seek(0)

            $decoder = Await-AsyncOperation `
                -Operation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) `
                -ResultType ([Windows.Graphics.Imaging.BitmapDecoder])
            $bitmap = Await-AsyncOperation `
                -Operation ($decoder.GetSoftwareBitmapAsync()) `
                -ResultType ([Windows.Graphics.Imaging.SoftwareBitmap])
            $ocrResult = Await-AsyncOperation `
                -Operation ($ocrEngine.RecognizeAsync($bitmap)) `
                -ResultType ([Windows.Media.Ocr.OcrResult])

            $parts.Add("=== PAGE $($pageIndex + 1) ===")
            $parts.Add($ocrResult.Text.Trim())
            $parts.Add("")
        }
        finally {
            if ($null -ne $page) {
                $page.Dispose()
            }
        }
    }

    return ($parts -join [Environment]::NewLine).Trim()
}

$null = New-Item -ItemType Directory -Force -Path $OutputDir

Get-ChildItem -Path $InputDir -Filter "C*.pdf" | Sort-Object Name | ForEach-Object {
    $pdfPath = $_.FullName
    $txtPath = Join-Path $OutputDir ($_.BaseName + ".txt")
    Write-Host "OCR:" $_.Name
    $text = Get-OcrTextForPdf -PdfPath $pdfPath
    Set-Content -Path $txtPath -Value $text -Encoding UTF8
}
