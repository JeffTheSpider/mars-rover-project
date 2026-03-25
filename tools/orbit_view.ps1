param(
    [string]$Direction = "front"  # front, top, side
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class OrbitHelper {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, IntPtr dwExtraInfo);

    public const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    public const uint MOUSEEVENTF_MIDDLEUP = 0x0040;
    public const uint MOUSEEVENTF_MOVE = 0x0001;

    public static void MiddleDrag(int startX, int startY, int endX, int endY, int steps) {
        SetCursorPos(startX, startY);
        System.Threading.Thread.Sleep(100);
        mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(50);

        for (int i = 1; i <= steps; i++) {
            int x = startX + (endX - startX) * i / steps;
            int y = startY + (endY - startY) * i / steps;
            SetCursorPos(x, y);
            System.Threading.Thread.Sleep(10);
        }

        System.Threading.Thread.Sleep(50);
        mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, IntPtr.Zero);
    }
}
"@

# Focus Fusion 360
$target = [IntPtr]0x000308EA
$foreground = [OrbitHelper]::GetForegroundWindow()
$dummy = 0
$foreThread = [OrbitHelper]::GetWindowThreadProcessId($foreground, [ref]$dummy)
$targetThread = [OrbitHelper]::GetWindowThreadProcessId($target, [ref]$dummy)
$curThread = [OrbitHelper]::GetCurrentThreadId()
[OrbitHelper]::AttachThreadInput($curThread, $foreThread, $true)
[OrbitHelper]::AttachThreadInput($curThread, $targetThread, $true)
[OrbitHelper]::SetForegroundWindow($target)
[OrbitHelper]::BringWindowToTop($target)
[OrbitHelper]::AttachThreadInput($curThread, $foreThread, $false)
[OrbitHelper]::AttachThreadInput($curThread, $targetThread, $false)
Start-Sleep -Milliseconds 500

# Window is at (0,0) 1920x1080, center of viewport ~ (960, 540)
$cx = 960
$cy = 500

switch ($Direction) {
    "front" {
        # Orbit to front view: drag right and up
        [OrbitHelper]::MiddleDrag($cx, $cy, ($cx + 300), ($cy - 100), 30)
    }
    "top" {
        # Orbit to top view: drag upward significantly
        [OrbitHelper]::MiddleDrag($cx, $cy, $cx, ($cy - 350), 30)
    }
    "side" {
        # Orbit to side view: drag left
        [OrbitHelper]::MiddleDrag($cx, $cy, ($cx - 400), $cy, 30)
    }
    "reset" {
        # Orbit back to isometric
        [OrbitHelper]::MiddleDrag($cx, $cy, ($cx + 200), ($cy - 200), 30)
    }
}

Start-Sleep -Milliseconds 500
Write-Host "Orbited to $Direction view"
