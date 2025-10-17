# Windows 방화벽에 포트 3000 허용 규칙 추가
# 이 스크립트는 관리자 권한으로 실행해야 합니다

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Firewall Checker Web - 방화벽 설정 스크립트" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ 오류: 이 스크립트는 관리자 권한으로 실행해야 합니다!" -ForegroundColor Red
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Yellow
    Write-Host "1. PowerShell을 마우스 우클릭" -ForegroundColor Yellow
    Write-Host "2. '관리자 권한으로 실행' 선택" -ForegroundColor Yellow
    Write-Host "3. 스크립트 다시 실행" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

# 기존 규칙 확인
$existingRule = Get-NetFirewallRule -DisplayName "Firewall Checker Web" -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "⚠️  기존 방화벽 규칙이 이미 존재합니다." -ForegroundColor Yellow
    $response = Read-Host "기존 규칙을 삭제하고 새로 만들까요? (Y/N)"

    if ($response -eq "Y" -or $response -eq "y") {
        Remove-NetFirewallRule -DisplayName "Firewall Checker Web"
        Write-Host "✓ 기존 규칙 삭제 완료" -ForegroundColor Green
    } else {
        Write-Host "취소되었습니다." -ForegroundColor Yellow
        pause
        exit
    }
}

# 방화벽 규칙 추가
try {
    New-NetFirewallRule `
        -DisplayName "Firewall Checker Web" `
        -Description "Allows inbound TCP traffic on port 3000 for Firewall Checker Web application" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 3000 `
        -Action Allow `
        -Profile Any `
        -Enabled True

    Write-Host ""
    Write-Host "✓ 방화벽 규칙이 성공적으로 추가되었습니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "설정 내용:" -ForegroundColor Cyan
    Write-Host "  - 규칙 이름: Firewall Checker Web" -ForegroundColor White
    Write-Host "  - 포트: 3000" -ForegroundColor White
    Write-Host "  - 프로토콜: TCP" -ForegroundColor White
    Write-Host "  - 방향: 인바운드" -ForegroundColor White
    Write-Host "  - 동작: 허용" -ForegroundColor White
    Write-Host ""
    Write-Host "이제 다른 PC에서 접속할 수 있습니다!" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "❌ 오류: 방화벽 규칙 추가 실패" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

Write-Host "=================================================" -ForegroundColor Cyan
pause
