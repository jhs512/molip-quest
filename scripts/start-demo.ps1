param([switch]$Instructor)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$demoRoot = Join-Path $projectRoot 'target/demo'
New-Item -ItemType Directory -Force -Path $demoRoot | Out-Null
$demoBin = Join-Path $demoRoot 'bin'
New-Item -ItemType Directory -Force -Path $demoBin | Out-Null
foreach ($binary in @('molip-server.exe','molip-quest.exe')) {
    $destination = Join-Path $demoBin $binary
    if (!(Test-Path $destination)) { Copy-Item -LiteralPath (Join-Path $projectRoot "target/debug/$binary") -Destination $destination }
}
$baseUrl = 'http://127.0.0.1:3010'
$demoPassword = 'MolipQuest-Demo-2026!'
function Invoke-DemoApi($Method, $Path, $Body, $Token) {
    $request = @{ Method = $Method; Uri = "$baseUrl$Path"; ContentType = 'application/json' }
    if ($Body) { $request.Body = [System.Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 30 -Compress)) }
    if ($Token) { $request.Headers = @{ Authorization = "Bearer $Token" } }
    Invoke-RestMethod @request
}
$environmentNames = @('DATABASE_URL','MOLIP_INSTRUCTOR_EMAIL','MOLIP_INSTRUCTOR_PASSWORD','MOLIP_SERVER_BIND','MOLIP_SERVER_URL','MOLIP_DEMO_EMAIL','MOLIP_DEMO_PASSWORD','MOLIP_DEMO_CLASSROOM','MOLIP_DEMO_COURSE')
$savedEnvironment = @{}
foreach ($name in $environmentNames) { $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
try {
    $listener = Get-NetTCPConnection -LocalPort 3010 -State Listen -ErrorAction SilentlyContinue
    if (!$listener) {
        $env:DATABASE_URL = 'sqlite://server.sqlite3?mode=rwc'
        $env:MOLIP_INSTRUCTOR_EMAIL = 'teacher@molip.local'
        $env:MOLIP_INSTRUCTOR_PASSWORD = $demoPassword
        $env:MOLIP_SERVER_BIND = '127.0.0.1:3010'
        $server = Start-Process -FilePath (Join-Path $demoBin 'molip-server.exe') -WorkingDirectory $demoRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $demoRoot 'server.log') -RedirectStandardError (Join-Path $demoRoot 'server-error.log') -PassThru
        $server.Id | Set-Content (Join-Path $demoRoot 'server.pid')
    }
    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        try { Invoke-RestMethod "$baseUrl/api/health" -TimeoutSec 1 | Out-Null; $ready = $true; break } catch { Start-Sleep -Milliseconds 250 }
    }
    if (!$ready) { throw 'Local demo server did not become ready. Check target/demo/server-error.log.' }
    $teacher = Invoke-DemoApi POST '/api/login' @{email='teacher@molip.local'; password=$demoPassword} $null
    $course = Get-Content -Raw -Encoding UTF8 (Join-Path $projectRoot 'courses/getting-started.json') | ConvertFrom-Json
    $courses = Invoke-DemoApi GET '/api/courses' $null $teacher.token
    if (!($courses | Where-Object { $_.id -eq $course.id })) { Invoke-DemoApi POST '/api/courses' $course $teacher.token | Out-Null }
    $classroom = Invoke-DemoApi GET '/api/classrooms' $null $teacher.token | ForEach-Object { $_ } | Where-Object { $_.id } | Select-Object -First 1
    if (!$classroom) { $classroom = Invoke-DemoApi POST '/api/classrooms' @{title='Python 첫 걸음'} $teacher.token }
    Invoke-DemoApi POST "/api/classrooms/$($classroom.id)/assign" @{course_id=$course.id} $teacher.token | Out-Null
    if (!$Instructor) {
        try { Invoke-DemoApi POST '/api/register' @{email='student@molip.local';password=$demoPassword} $null | Out-Null }
        catch { if ([int]$_.Exception.Response.StatusCode -ne 409) { throw } }
        $student = Invoke-DemoApi POST '/api/login' @{email='student@molip.local';password=$demoPassword} $null
        Invoke-DemoApi POST '/api/join' @{invite=$classroom.invite} $student.token | Out-Null
    }
    $env:MOLIP_SERVER_URL = $baseUrl
    $env:MOLIP_DEMO_EMAIL = if ($Instructor) {'teacher@molip.local'} else {'student@molip.local'}
    $env:MOLIP_DEMO_PASSWORD = $demoPassword
    $env:MOLIP_DEMO_CLASSROOM = $classroom.id
    $env:MOLIP_DEMO_COURSE = if ($Instructor) {''} else {$course.id}
    $app = Start-Process -FilePath (Join-Path $demoBin 'molip-quest.exe') -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $demoRoot 'app.log') -RedirectStandardError (Join-Path $demoRoot 'app-error.log') -PassThru
    $app.Id | Set-Content (Join-Path $demoRoot 'app.pid')
    Write-Output "Demo app launched. Process: $($app.Id). Mode: $(if ($Instructor) {'instructor'} else {'student'})."
} finally {
    foreach ($name in $environmentNames) { [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process') }
}

