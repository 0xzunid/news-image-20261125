"""25 November 2026 news-image entry.

The grader runs this file. It takes the front page bundled with the
repository (``entry.png``) and places an exact copy in the output
directory (``$MAKEFUN_OUTPUT_DIR``, default ``/output``), then proves
the placed copy is genuine: same SHA-256 as the pinned digest and a
PNG header that says 1024x1024.

Python standard library only. No network, no arguments, no randomness.
"""

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
EXPECTED_SIZE = (1024, 1024)
# SHA-256 of entry.png as drawn on 2026-11-25. A damaged or swapped
# bundled image fails here before anything is reported as done.
EXPECTED_SHA256 = "8bee7a4a57ea045a7ad21363f30854d9ece4ee34c9658450d2c8c8113be51feb"


def file_sha256(path):
    """Hex SHA-256 of a file, read in 64 KiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(1 << 16)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def png_size(path):
    """(width, height) from the PNG IHDR chunk, or None if not a PNG."""
    with open(path, "rb") as f:
        head = f.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def verify_placed(placed):
    """True when the placed copy is a genuine 1024x1024 copy of the bundle.

    Checks the PNG header size first, then the digest of the placed copy
    and of the bundled original, so a damaged bundle fails here too.
    """
    if png_size(placed) != EXPECTED_SIZE:
        print(f"bad size {png_size(placed)}, expected {EXPECTED_SIZE}",
              file=sys.stderr)
        return False
    if file_sha256(placed) != EXPECTED_SHA256:
        print("placed copy digest mismatch", file=sys.stderr)
        return False
    if file_sha256(SOURCE) != EXPECTED_SHA256:
        print("bundled image digest mismatch", file=sys.stderr)
        return False
    return True


def run():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    placed = DEST_DIR / "entry.png"
    shutil.copyfile(SOURCE, placed)

    if not verify_placed(placed):
        return 1

    print(f"wrote {placed} ({placed.stat().st_size} bytes, "
          f"{EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
