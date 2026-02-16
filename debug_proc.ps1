Get-Process python | ForEach-Object {
    $parent = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").ParentProcessId
    [PSCustomObject]@{
        Id = $_.Id
        ParentId = $parent
        CommandLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    }
} | Format-List
