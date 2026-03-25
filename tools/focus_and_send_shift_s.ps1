Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FocusHelper {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
}
"@

$target = [IntPtr]0x000308EA
$foreground = [FocusHelper]::GetForegroundWindow()

# Attach to the foreground thread to bypass focus restrictions
$dummy = 0
$foreThread = [FocusHelper]::GetWindowThreadProcessId($foreground, [ref]$dummy)
$targetThread = [FocusHelper]::GetWindowThreadProcessId($target, [ref]$dummy)
$curThread = [FocusHelper]::GetCurrentThreadId()

[FocusHelper]::AttachThreadInput($curThread, $foreThread, $true)
[FocusHelper]::AttachThreadInput($curThread, $targetThread, $true)
[FocusHelper]::SetForegroundWindow($target)
[FocusHelper]::BringWindowToTop($target)
[FocusHelper]::AttachThreadInput($curThread, $foreThread, $false)
[FocusHelper]::AttachThreadInput($curThread, $targetThread, $false)

Start-Sleep -Milliseconds 800
Write-Host "Fusion 360 should be focused now"

# Send Shift+S
[System.Windows.Forms.SendKeys]::SendWait('+s')
Write-Host "Sent Shift+S"
Start-Sleep -Seconds 3
Write-Host "Done - dialog should be open"
