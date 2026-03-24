Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseOK {
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, IntPtr dwExtraInfo);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public static void Click(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(100);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(50);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, IntPtr.Zero);
    }
}
"@

$root = [System.Windows.Automation.AutomationElement]::RootElement
$fusionProc = Get-Process -Name 'Fusion360' | Select-Object -First 1
$fusionWin = $root.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $fusionProc.Id
    )
)

# Find buttons
$buttonCond = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::LocalizedControlTypeProperty, 'button'
)
$buttons = $fusionWin.FindAll([System.Windows.Automation.TreeScope]::Descendants, $buttonCond)
Write-Host "Found $($buttons.Count) buttons:"
foreach ($btn in $buttons) {
    $name = $btn.Current.Name
    $rect = $btn.Current.BoundingRectangle
    Write-Host "  '$name' at ($([int]$rect.X),$([int]$rect.Y)) $([int]$rect.Width)x$([int]$rect.Height)"
    if ($name -match 'OK|Close|Yes|Accept') {
        $cx = [int]($rect.X + $rect.Width / 2)
        $cy = [int]($rect.Y + $rect.Height / 2)
        Write-Host "  -> Clicking '$name' at ($cx, $cy)"
        try {
            $invokePattern = $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
            $invokePattern.Invoke()
            Write-Host "  -> Invoked via pattern"
        } catch {
            [MouseOK]::Click($cx, $cy)
            Write-Host "  -> Clicked via mouse"
        }
        break
    }
}
