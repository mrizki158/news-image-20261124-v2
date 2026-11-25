#!/usr/bin/env python3
"""news-image-20261124 v2 entry.

Copies the pre-rendered entry.png (produced by build_image.py, committed
in this repo) to the output directory.

Stdlib only. Output directory comes from MAKEFUN_OUTPUT_DIR, default /output.
"""
import os
import shutil


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
