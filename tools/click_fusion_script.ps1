# click_fusion_script.ps1 - Use Windows UI Automation to find and run a Fusion 360 script
# Usage: powershell -File click_fusion_script.ps1 -ScriptName "BatchExportAll"
param(
    [string]$ScriptName = "BatchExportAll"
)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

# Helper: recursive search for elements containing text
function Find-ElementByName {
    param(
        [System.Windows.Automation.AutomationElement]$Parent,
        [string]$Name,
        [int]$MaxDepth = 10
    )
    if ($MaxDepth -le 0) { return $null }

    $condition = [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::NameProperty, $Name
    )
    $found = $Parent.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
    return $found
}

function Find-ElementBySubstring {
    param(
        [System.Windows.Automation.AutomationElement]$Parent,
        [string]$Substring,
        [int]$MaxResults = 20
    )
    $all = $Parent.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition
    )
    $results = @()
    foreach ($elem in $all) {
        try {
            $name = $elem.Current.Name
            if ($name -and $name -like "*$Substring*") {
                $rect = $elem.Current.BoundingRectangle
                $results += [PSCustomObject]@{
                    Name = $name
                    ControlType = $elem.Current.LocalizedControlType
                    X = [int]$rect.X
                    Y = [int]$rect.Y
                    Width = [int]$rect.Width
                    Height = [int]$rect.Height
                    CenterX = [int]($rect.X + $rect.Width / 2)
                    CenterY = [int]($rect.Y + $rect.Height / 2)
                    Element = $elem
                }
                if ($results.Count -ge $MaxResults) { break }
            }
        } catch { }
    }
    return $results
}

# Get Fusion 360 process
$fusionProc = Get-Process -Name "Fusion360" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $fusionProc) {
    Write-Host "ERROR: Fusion 360 not running"
    exit 1
}
Write-Host "Found Fusion 360 PID: $($fusionProc.Id)"

# Get root automation element
$root = [System.Windows.Automation.AutomationElement]::RootElement

# Find the Fusion 360 main window
$fusionWin = $root.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $fusionProc.Id
    )
)
if (-not $fusionWin) {
    Write-Host "ERROR: Could not find Fusion 360 window via UI Automation"
    exit 1
}
Write-Host "Found Fusion 360 window: $($fusionWin.Current.Name)"

# Search for the Scripts and Add-Ins dialog (it's a child window or pane)
Write-Host "`nSearching for '$ScriptName' in UI tree..."
$matches = Find-ElementBySubstring -Parent $fusionWin -Substring $ScriptName
if ($matches.Count -eq 0) {
    Write-Host "No elements found containing '$ScriptName'"
    Write-Host "`nSearching for 'Scripts' dialog elements..."
    $dialogMatches = Find-ElementBySubstring -Parent $fusionWin -Substring "Scripts"
    foreach ($m in $dialogMatches) {
        Write-Host "  Found: '$($m.Name)' [$($m.ControlType)] at ($($m.X),$($m.Y)) size $($m.Width)x$($m.Height)"
    }
    exit 1
}

Write-Host "`nFound $($matches.Count) elements matching '$ScriptName':"
foreach ($m in $matches) {
    Write-Host "  '$($m.Name)' [$($m.ControlType)] at ($($m.X),$($m.Y)) size $($m.Width)x$($m.Height) center=($($m.CenterX),$($m.CenterY))"
}

# Try to select/click the first matching element
$target = $matches[0]
Write-Host "`nAttempting to interact with: '$($target.Name)' [$($target.ControlType)]"

# Try InvokePattern first
try {
    $invokePattern = $target.Element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    Write-Host "Invoking element..."
    $invokePattern.Invoke()
    Write-Host "SUCCESS: Invoked '$($target.Name)'"
    exit 0
} catch {
    Write-Host "InvokePattern not available: $($_.Exception.Message)"
}

# Try SelectionItemPattern
try {
    $selectPattern = $target.Element.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
    Write-Host "Selecting element..."
    $selectPattern.Select()
    Write-Host "SUCCESS: Selected '$($target.Name)'"
    exit 0
} catch {
    Write-Host "SelectionItemPattern not available: $($_.Exception.Message)"
}

# Fallback: click at center coordinates
Write-Host "Falling back to click at center: ($($target.CenterX), $($target.CenterY))"
[System.Windows.Forms.Cursor]::Position = [System.Drawing.Point]::new($target.CenterX, $target.CenterY)
Start-Sleep -Milliseconds 100

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseClick {
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, IntPtr dwExtraInfo);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
}
"@

[MouseClick]::mouse_event([MouseClick]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 50
[MouseClick]::mouse_event([MouseClick]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [IntPtr]::Zero)
Write-Host "SUCCESS: Clicked at ($($target.CenterX), $($target.CenterY))"
