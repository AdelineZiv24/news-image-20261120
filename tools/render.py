#!/usr/bin/env python3
"""Render frontpage.html to entry.png with the Chromium headless shell.

The front page is a fixed 1024x1024 HTML canvas; this script screenshots it
at exactly that size so the PNG the entry ships is the page the judge sees.
It looks for a Chromium binary in the Playwright cache (or on PATH) and
needs no network.

Usage: python3 tools/render.py [--html frontpage.html] [--out entry.png]
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_chromium() -> str:
    candidates = sorted(
        glob.glob(
            os.path.expanduser(
                "~/.cache/ms-playwright/chromium_headless_shell-*/"
                "chrome-headless-shell-linux64/chrome-headless-shell"
            )
        )
        + glob.glob(
            os.path.expanduser(
                "~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"
            )
        )
    )
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("no Chromium binary found (looked in ~/.cache/ms-playwright and PATH)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", default=str(ROOT / "frontpage.html"))
    parser.add_argument("--out", default=str(ROOT / "entry.png"))
    args = parser.parse_args()

    chromium = find_chromium()
    html_uri = Path(args.html).resolve().as_uri()
    cmd = [
        chromium,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1024,1024",
        "--virtual-time-budget=8000",
        f"--screenshot={args.out}",
        html_uri,
    ]
    print("running:", " ".join(cmd[:3]), "...")
    subprocess.run(cmd, check=True)
    size = Path(args.out).stat().st_size
    print(f"wrote {args.out} ({size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
