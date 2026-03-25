param(
    [string]$ViewName = "front",
    [string]$OutputFile = "D:\Mars Rover Project\temp_view.png"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ViewHelper {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
}
"@

$target = [IntPtr]0x000308EA
$foreground = [ViewHelper]::GetForegroundWindow()
$dummy = 0
$foreThread = [ViewHelper]::GetWindowThreadProcessId($foreground, [ref]$dummy)
$targetThread = [ViewHelper]::GetWindowThreadProcessId($target, [ref]$dummy)
$curThread = [ViewHelper]::GetCurrentThreadId()

[ViewHelper]::AttachThreadInput($curThread, $foreThread, $true)
[ViewHelper]::AttachThreadInput($curThread, $targetThread, $true)
[ViewHelper]::SetForegroundWindow($target)
[ViewHelper]::BringWindowToTop($target)
Start-Sleep -Milliseconds 500

# Send view shortcut based on view name
# Fusion 360 view shortcuts: look at view cube
switch ($ViewName) {
    "front"  { [System.Windows.Forms.SendKeys]::SendWait("{F6}"); Start-Sleep -Milliseconds 300 }
    "top"    { }
    "side"   { }
}

[ViewHelper]::AttachThreadInput($curThread, $foreThread, $false)
[ViewHelper]::AttachThreadInput($curThread, $targetThread, $false)

Start-Sleep -Milliseconds 1000
Write-Host "View changed to $ViewName"
