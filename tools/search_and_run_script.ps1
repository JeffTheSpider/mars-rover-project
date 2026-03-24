# search_and_run_script.ps1 - Clear search, type filter, click to select and run
param(
    [string]$ScriptName = "BatchExportAll"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseHelper {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern bool GetCursorPos(out POINT lpPoint);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, IntPtr dwExtraInfo);

    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const uint MOUSEEVENTF_LEFTCLICK = 0x0006;

    [StructLayout(LayoutKind.Sequential)]
    public struct POINT {
        public int X;
        public int Y;
    }

    public static void Click(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(100);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(50);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, IntPtr.Zero);
    }

    public static void DoubleClick(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(100);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(30);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(50);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(30);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, IntPtr.Zero);
    }
}
"@

# Step 1: Get dialog position from UI Automation
$root = [System.Windows.Automation.AutomationElement]::RootElement
$fusionProc = Get-Process -Name 'Fusion360' | Select-Object -First 1
$fusionWin = $root.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $fusionProc.Id
    )
)

$dialogCond = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::NameProperty, 'Scripts and Add-Ins'
)
$dialog = $fusionWin.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $dialogCond)
if (-not $dialog) {
    Write-Host "ERROR: Scripts and Add-Ins dialog not found"
    exit 1
}
$dialogRect = $dialog.Current.BoundingRectangle
Write-Host "Dialog at ($([int]$dialogRect.X),$([int]$dialogRect.Y)) $([int]$dialogRect.Width)x$([int]$dialogRect.Height)"

# Step 2: Find the search TextField
$editCond = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::LocalizedControlTypeProperty, 'edit'
)
$searchField = $dialog.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $editCond)
if ($searchField) {
    $sfRect = $searchField.Current.BoundingRectangle
    Write-Host "Search field at ($([int]$sfRect.X),$([int]$sfRect.Y)) $([int]$sfRect.Width)x$([int]$sfRect.Height)"

    # Click on the search field to focus it
    $sfCenterX = [int]($sfRect.X + $sfRect.Width / 2)
    $sfCenterY = [int]($sfRect.Y + $sfRect.Height / 2)
    Write-Host "Clicking search field at ($sfCenterX, $sfCenterY)"
    [MouseHelper]::Click($sfCenterX, $sfCenterY)
    Start-Sleep -Milliseconds 300

    # Triple-click to select all text
    [MouseHelper]::Click($sfCenterX, $sfCenterY)
    Start-Sleep -Milliseconds 50
    [MouseHelper]::Click($sfCenterX, $sfCenterY)
    Start-Sleep -Milliseconds 50
    [MouseHelper]::Click($sfCenterX, $sfCenterY)
    Start-Sleep -Milliseconds 200

    # Also use Ctrl+A to be safe
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 200

    # Type the script name to filter
    [System.Windows.Forms.SendKeys]::SendWait($ScriptName)
    Start-Sleep -Milliseconds 800
    Write-Host "Typed '$ScriptName' into search field"
} else {
    Write-Host "WARNING: Search field not found, proceeding anyway"
}

# Step 3: Now we need to click on the first result in the list
# The list area is in the right portion of the dialog
# Based on the dialog layout, the first list item is approximately:
# X: dialog left + left panel width + name column offset
# Y: dialog top + title bar + search + column headers + first row
$listFirstRowX = [int]($dialogRect.X + 470)  # Name column area
$listFirstRowY = [int]($dialogRect.Y + 130)   # First data row
Write-Host "Estimated first row position: ($listFirstRowX, $listFirstRowY)"

# Click on the first list item to select it
Write-Host "Clicking first list item..."
[MouseHelper]::Click($listFirstRowX, $listFirstRowY)
Start-Sleep -Milliseconds 500

# Step 4: Take stock - check if the detail pane now shows info
# Try to double-click to run it
Write-Host "Double-clicking to run..."
[MouseHelper]::DoubleClick($listFirstRowX, $listFirstRowY)
Start-Sleep -Milliseconds 500

Write-Host "Done - check Fusion 360 for results"
