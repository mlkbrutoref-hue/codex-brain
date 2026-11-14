"""Phone Link discovery does not install, log in, or infer device connection."""
import json
import os
import subprocess
from datetime import datetime, timezone


def discover_phone_link():
    result = dict(checked_at=datetime.now(timezone.utc).isoformat(), phone_link_found="NOT_CHECKED",
                  phone_connected="UNKNOWN", screen_mirroring="UNKNOWN", apps_available="UNKNOWN",
                  instagram_accessible="NOT_TESTED", tiktok_accessible="NOT_TESTED", evidence=[])
    if os.name != "nt":
        result["evidence"].append("Windows required")
        return result
    script = "$ErrorActionPreference='Stop'; $items=@(Get-AppxPackage -Name Microsoft.YourPhone); ConvertTo-Json -InputObject @{count=$items.Count; packages=@($items | Select-Object Name,Version,Status)} -Depth 4 -Compress"
    try:
        completed = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                                   capture_output=True, text=True, timeout=45, check=True)
        packages = json.loads(completed.stdout)
        result["phone_link_found"] = "YES" if packages["count"] else "NO"
        result["evidence"].append(dict(source="Get-AppxPackage/current_user", result=packages))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result["evidence"].append(dict(error=type(exc).__name__, meaning="Discovery failed; absence not established"))
    return result


if __name__ == "__main__":
    print(json.dumps(discover_phone_link(), ensure_ascii=False, indent=2))
