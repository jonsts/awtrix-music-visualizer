"""Register (or unregister) a Windows Task Scheduler task that starts the
visualizer at user login.

Usage:
    python install_autostart.py              # install the scheduled task
    python install_autostart.py --remove     # remove it
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TASK_NAME = "AwtrixMusicVisualizer"
PROJECT_DIR = Path(__file__).resolve().parent


def install():
    python = sys.executable
    config = PROJECT_DIR / "config.toml"

    # schtasks XML is the most reliable way to create a task with the right
    # settings (run at logon, hidden window, no time limit).
    xml = f"""\
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Hidden>true</Hidden>
    <AllowStartOnDemand>true</AllowStartOnDemand>
  </Settings>
  <Actions>
    <Exec>
      <Command>{python}</Command>
      <Arguments>-m visualizer --config "{config}"</Arguments>
      <WorkingDirectory>{PROJECT_DIR}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    xml_path = PROJECT_DIR / "_task.xml"
    xml_path.write_text(xml, encoding="utf-16")

    result = subprocess.run(
        ["schtasks", "/Create", "/TN", TASK_NAME, "/XML", str(xml_path), "/F"],
        capture_output=True,
        text=True,
    )
    xml_path.unlink()

    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' created. The visualizer will start on login.")
        print(f"  To run now:   schtasks /Run /TN {TASK_NAME}")
        print(f"  To stop:      schtasks /End /TN {TASK_NAME}")
        print(f"  To remove:    python install_autostart.py --remove")
    else:
        print("Failed to create task:", result.stderr.strip(), file=sys.stderr)
        return 1
    return 0


def remove():
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' removed.")
    else:
        print("Failed to remove task:", result.stderr.strip(), file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Install/remove autostart task")
    parser.add_argument("--remove", action="store_true", help="remove the task")
    args = parser.parse_args()
    raise SystemExit(remove() if args.remove else install())


if __name__ == "__main__":
    main()
