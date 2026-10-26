#!/usr/bin/env python3
"""Poll an HTTP endpoint without leaking transient curl failures."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
def check_http(curl: str, url: str, *, verbose: bool) -> bool:
    command = [curl, "--fail", "--silent"]
    if verbose:
        command.append("--show-error")
    command.extend(["--output", "/dev/null", url])
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=None if verbose else subprocess.DEVNULL,
    ).returncode == 0


def wait_for_http(curl: str, url: str, attempts: int, interval: float) -> int:
    for attempt in range(1, attempts + 1):
        # Startup failures are expected while the container is still booting.
        if check_http(curl, url, verbose=False):
            break
        if attempt < attempts:
            time.sleep(interval)
    else:
        print(f"container did not become ready after {attempts} attempts", file=sys.stderr)
        return 1

    # Always perform a visible final check so a late failure cannot be hidden by
    # a transient successful probe or by the polling loop's suppressed errors.
    if check_http(curl, url, verbose=True):
        return 0
    print("container readiness check failed", file=sys.stderr)
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--attempts", type=int, default=30)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--curl", default="curl")
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error("--attempts must be at least 1")
    if args.interval < 0:
        parser.error("--interval must not be negative")
    return args


def main() -> int:
    args = parse_args()
    return wait_for_http(args.curl, args.url, args.attempts, args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
