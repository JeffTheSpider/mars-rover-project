Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinHelper {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$hwnd = [IntPtr]0x000308EA
[WinHelper]::ShowWindow($hwnd, 9)  # SW_RESTORE
Start-Sleep -Milliseconds 500
[WinHelper]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait('+s')
Write-Host "Activated Fusion 360 and sent Shift+S to open Scripts dialog"
Start-Sleep -Seconds 2
Write-Host "Dialog should be open now"
