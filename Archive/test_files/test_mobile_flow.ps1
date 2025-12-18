# QUICK TEST: Mobile Signup & Web Activation
# Run these commands one by one in PowerShell

# ============================================================
# STEP 1: Create user via API (simulating mobile signup)
# ============================================================

$signupData = @{
    username = "testmobile1"
    email = "testmobile1@example.com"
    password = "MobilePass123!"
    confirm_password = "MobilePass123!"
    first_name = "Mobile"
    last_name = "Tester"
    phone = "+254712345678"
    role = "tenant"
} | ConvertTo-Json

Write-Host "`n[STEP 1] Creating user via API..." -ForegroundColor Cyan
$signupResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/signup/" -Method POST -Body $signupData -ContentType "application/json"
Write-Host "`n✅ User Created:" -ForegroundColor Green
$signupResponse | ConvertTo-Json -Depth 5

# ============================================================
# STEP 2: Try to login BEFORE activation (should fail)
# ============================================================

$loginData = @{
    email = "testmobile1@example.com"
    password = "MobilePass123!"
} | ConvertTo-Json

Write-Host "`n[STEP 2] Trying to login BEFORE activation..." -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login/" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "`n⚠️ Unexpected: Login succeeded (should have failed)" -ForegroundColor Yellow
    $loginResponse | ConvertTo-Json -Depth 5
} catch {
    $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "`n✅ Expected: Login blocked" -ForegroundColor Green
    Write-Host "Message: $($errorResponse.message)" -ForegroundColor Yellow
}

# ============================================================
# STEP 3: ACTIVATE USER ON WEB
# ============================================================

Write-Host "`n[STEP 3] NOW ACTIVATE THE USER ON WEB:" -ForegroundColor Magenta
Write-Host "1. Open browser: http://127.0.0.1:8000/login/" -ForegroundColor White
Write-Host "2. Login as admin" -ForegroundColor White
Write-Host "3. Go to: User Management → User" -ForegroundColor White
Write-Host "4. Find user: testmobile1" -ForegroundColor White
Write-Host "5. Click 'Activate' button" -ForegroundColor White
Write-Host "`nPress ENTER after activating the user..." -ForegroundColor Yellow
Read-Host

# ============================================================
# STEP 4: Try to login AFTER activation (should succeed)
# ============================================================

Write-Host "`n[STEP 4] Trying to login AFTER activation..." -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login/" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "`n✅ SUCCESS: Login successful!" -ForegroundColor Green
    Write-Host "Access Token: $($loginResponse.access.Substring(0, 50))..." -ForegroundColor White
    Write-Host "User ID: $($loginResponse.user.id)" -ForegroundColor White
    Write-Host "Username: $($loginResponse.user.username)" -ForegroundColor White
    
    # Store token for next step
    $global:accessToken = $loginResponse.access
    
} catch {
    $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "`n❌ FAILED: Login still blocked" -ForegroundColor Red
    Write-Host "Message: $($errorResponse.message)" -ForegroundColor Yellow
}

# ============================================================
# STEP 5: Make authenticated request (test JWT token)
# ============================================================

if ($global:accessToken) {
    Write-Host "`n[STEP 5] Making authenticated request..." -ForegroundColor Cyan
    
    $headers = @{
        "Authorization" = "Bearer $global:accessToken"
        "Content-Type" = "application/json"
    }
    
    try {
        $profileResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/profile/" -Method GET -Headers $headers
        Write-Host "`n✅ SUCCESS: Authenticated request works!" -ForegroundColor Green
        $profileResponse | ConvertTo-Json -Depth 5
    } catch {
        Write-Host "`n❌ FAILED: Authenticated request failed" -ForegroundColor Red
        Write-Host $_.ErrorDetails.Message
    }
}

# ============================================================
# SUMMARY
# ============================================================

Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                    TEST COMPLETE                           " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nTest Credentials:" -ForegroundColor Yellow
Write-Host "  Username: testmobile1" -ForegroundColor White
Write-Host "  Email: testmobile1@example.com" -ForegroundColor White
Write-Host "  Password: MobilePass123!" -ForegroundColor White
Write-Host "`nYou can use these credentials in your Flutter app!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan
