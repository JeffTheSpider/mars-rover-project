Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinApi {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);
}
"@

# Use the known Fusion 360 window handle directly
$hwnd = [IntPtr]0x000308EA
$isWin = [WinApi]::IsWindow($hwnd)
Write-Host "Is valid window: $isWin"

if (-not $isWin) {
    Write-Host "Window handle invalid"
    exit 1
}

# Bring to foreground
$result = [WinApi]::SetForegroundWindow($hwnd)
Write-Host "SetForegroundWindow result: $result"
Start-Sleep -Milliseconds 1000

# Send Shift+S
[System.Windows.Forms.SendKeys]::SendWait("+s")
Write-Host "Sent Shift+S"
Start-Sleep -Milliseconds 500
Write-Host "Done"
