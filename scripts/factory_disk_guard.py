#!/usr/bin/env python3
from shutil import disk_usage
from pathlib import Path
import sys

THRESHOLD_WARN = 80
THRESHOLD_BLOCK = 90


def get_usage_percent(path: str = "/"):
    total, used, free = disk_usage(path)
    return int((used / total) * 100)


def main():
    usage = get_usage_percent()
    print(f"DISK_USAGE={usage}%")

    if usage >= THRESHOLD_BLOCK:
        print("BLOCKED_DISK_CRITICAL")
        return 2
    elif usage >= THRESHOLD_WARN:
        print("WARNING_DISK_PRESSURE")
        return 1
    else:
        print("DISK_OK")
        return 0


if __name__ == "__main__":
    sys.exit(main())
