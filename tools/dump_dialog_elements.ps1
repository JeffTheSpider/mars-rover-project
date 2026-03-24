Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$fusionProc = Get-Process -Name 'Fusion360' | Select-Object -First 1
$fusionWin = $root.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $fusionProc.Id
    )
)

# Find the Scripts dialog
$dialogCond = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::NameProperty, 'Scripts and Add-Ins'
)
$dialog = $fusionWin.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $dialogCond)
if (-not $dialog) {
    Write-Host "ERROR: Scripts and Add-Ins dialog not found"
    exit 1
}
$r = $dialog.Current.BoundingRectangle
Write-Host "Dialog: '$($dialog.Current.Name)' at ($([int]$r.X),$([int]$r.Y)) $([int]$r.Width)x$([int]$r.Height)"

# Enumerate all descendants
$all = $dialog.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition
)
Write-Host "Total elements: $($all.Count)"
$i = 0
foreach ($elem in $all) {
    $i++
    try {
        $name = $elem.Current.Name
        $type = $elem.Current.LocalizedControlType
        $className = $elem.Current.ClassName
        $rect = $elem.Current.BoundingRectangle
        $autoId = $elem.Current.AutomationId
        if ($name -or $type -match 'button|list|item|text|edit|table|data|grid|tree|pane|group') {
            Write-Host "  [$i] '$name' [$type] class='$className' id='$autoId' at ($([int]$rect.X),$([int]$rect.Y)) $([int]$rect.Width)x$([int]$rect.Height)"
        }
    } catch { }
    if ($i -gt 300) { Write-Host '  ... (truncated at 300)'; break }
}
