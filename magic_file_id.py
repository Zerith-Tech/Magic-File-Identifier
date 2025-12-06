#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import json
from textwrap import shorten


# ==============
#  Color helpers
# ==============

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
DIM = "\033[2m";
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"

def color(text: str, *codes: str) -> str:
    """Wrap text in ANSI color codes."""
    if not codes:
        return text
    return "".join(codes) + text + RESET



# ==========================
#  Magic number "database"
# ==========================

MAGIC_NUMBERS = {
    # Images
    b"\x89PNG\r\n\x1a\n": "PNG image",
    b"\xFF\xD8\xFF": "JPEG image",
    b"GIF87a": "GIF image",
    b"GIF89a": "GIF image",
    b"BM": "BMP image",
    b"\x49\x49\x2A\x00": "TIFF image (little-endian)",
    b"\x4D\x4D\x00\x2A": "TIFF image (big-endian)",
    b"\x52\x49\x46\x46": "RIFF container (e.g., AVI, WAV, WEBP)",

    # Archives / compressed
    b"\x50\x4B\x03\x04": "ZIP archive (or DOCX/XLSX/PPTX, JAR, APK, etc.)",
    b"\x1F\x8B": "GZIP compressed data",
    b"\x42\x5A\x68": "BZIP2 compressed data",
    b"\x37\x7A\xBC\xAF\x27\x1C": "7-Zip archive",
    b"\x52\x61\x72\x21\x1A\x07\x00": "RAR archive v1.5–4.0",
    b"\x52\x61\x72\x21\x1A\x07\x01\x00": "RAR archive v5.0+",
    b"\x75\x73\x74\x61\x72": "TAR archive (ustar)",

    # Executables / binaries
    b"\x7FELF": "ELF binary (Linux)",
    b"MZ": "PE executable (Windows EXE/DLL)",

    # Documents / media
    b"%PDF": "PDF document",
    b"\x00\x00\x00\x18ftyp": "MP4 video",
    b"\x00\x00\x00 ftyp": "MP4 video",
    b"ID3": "MP3 audio (ID3 tag)",
}


# =====================
#  Core helper functions
# =====================

def detect_magic_type(header: bytes) -> str | None:
    """Return the detected file type based on magic numbers, or None if unknown."""
    for magic, ftype in MAGIC_NUMBERS.items():
        if header.startswith(magic):
            return ftype
    return None


def get_raw_hex(header: bytes, max_len: int = 64) -> str:
    """Return a hex string representation of the header, truncated for display."""
    hex_str = header.hex()
    return shorten(hex_str, width=max_len, placeholder="...")


def get_file_extension(path: str) -> str:
    """Return the file extension in lower case, including the dot (e.g., '.png')."""
    _, ext = os.path.splitext(path)
    return ext.lower()


def run_file_command(path: str) -> str:
    """Run the 'file' command on the given path and return its output."""
    try:
        result = subprocess.run(
            ["file", "--brief", path],
            capture_output=True,
            text=True,
            check=False,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode != 0:
            return f"Error running file: {err or 'unknown error'}"
        return out or "(no output from file)"
    except FileNotFoundError:
        return "'file' command not found on this system"
    except Exception as e:
        return f"Error running file command: {e}"



def extension_mismatch(file_ext: str, detected_type: str | None) -> bool:
    """Check for extension vs magic type mismatch."""
    if not file_ext or not detected_type:
        return False

    ext_map = {
        ".png": "PNG",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".gif": "GIF",
        ".bmp": "BMP",
        ".tif": "TIFF",
        ".tiff": "TIFF",
        ".pdf": "PDF",
        ".zip": "ZIP",
        ".gz": "GZIP",
        ".rar": "RAR",
        ".7z": "7-Zip",
        ".mp4": "MP4",
        ".mp3": "MP3",
        ".exe": "PE",
        ".dll": "PE",
    }

    expected_keyword = ext_map.get(file_ext)
    if not expected_keyword:
        return False

    return expected_keyword not in detected_type


# =====================
#  Analysis + printing
# =====================

def analyze_file(path: str, num_bytes: int) -> dict:
    """
    Perform the full analysis and return a dict with all results.
    Reusable for regular for text output and JSON.
    """
    result: dict = {
        "path": path,
        "exists": os.path.exists(path),
        "error": None,
        "magic": {
            "raw_hex": None,
            "detected_type": None,
        },
        "other": {
            "extension": None,
            "file_output": None,
        },
        "mismatch": False,
    }

    if not result["exists"]:
        result["error"] = "File does not exist."
        return result

    try:
        with open(path, "rb") as f:
            header = f.read(num_bytes)
    except Exception as e:
        result["error"] = f"Error reading file: {e}"
        return result

    raw_hex = get_raw_hex(header)
    detected_type = detect_magic_type(header)
    file_ext = get_file_extension(path)
    file_cmd_out = run_file_command(path)

    result["magic"]["raw_hex"] = raw_hex
    result["magic"]["detected_type"] = detected_type
    result["other"]["extension"] = file_ext or ""
    result["other"]["file_output"] = file_cmd_out

    result["mismatch"] = extension_mismatch(file_ext, detected_type)

    return result


def print_user(result: dict, quiet: bool) -> None:
    """Print colored view of the analysis result."""
    path = result["path"]
    print(color(f"=== {path} ===", BOLD, BLUE))

    if not result["exists"]:
        print(color("Error: file does not exist.\n", RED, BOLD))
        return

    if result["error"]:
        print(color(f"{result['error']}\n", RED, BOLD))
        return

    raw_hex = result["magic"]["raw_hex"]
    detected_type = result["magic"]["detected_type"] or "Unknown"
    file_ext = result["other"]["extension"] or "(none)"
    file_cmd_out = result["other"]["file_output"]

    print(color("Magic Number Analysis:", BOLD, CYAN))
    print(f"  Raw hex:        {color(str(raw_hex), DIM)}")
    print(f"  Detected type:  {color(detected_type, GREEN if detected_type != 'Unknown' else YELLOW)}")

    print()
    print(color("Other Info:", BOLD, CYAN))
    print(f"  File extension: {color(file_ext, CYAN)}")
    print(f"  file(1) output: {color(file_cmd_out, DIM)}")

    if result["mismatch"] and not quiet:
        print()
        print(color("[!] WARNING: Extension does NOT appear to match detected magic number type.",
                    BOLD, YELLOW))

    print()  # blank line between files


# ============
#  CLI / main
# ============

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "File type identification tool using magic numbers.\n\n"
            "The tool reads file headers (magic bytes) to determine the real\n"
            "file type, compares it with the file extension, and optionally\n"
            "returns structured JSON output for automation and piping."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Analyze a file (colored user-readable output):\n"
            "    python magic_file_id.py suspicious.jpg\n\n"
            "  Analyze multiple files:\n"
            "    python magic_file_id.py file1.bin file2.pdf\n\n"
            "  Read more header bytes:\n"
            "    python magic_file_id.py -n 64 image.png\n\n"
            "  Output text + JSON (useful for logs or mixed use):\n"
            "    python magic_file_id.py suspicious.jpg --json\n\n"
            "  Output JSON only (for automation / piping):\n"
            "    python magic_file_id.py suspicious.jpg --json-only | jq\n\n"
            "Notes:\n"
            "  • JSON-only mode suppresses all colored text output.\n"
            "  • Colors use ANSI escape codes (disable by redirecting or piping output).\n"
            "  • Mismatch warnings indicate extension vs magic-number disagreement."
        ),
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        help="File(s) to analyze",
    )
    parser.add_argument(
        "-n",
        "--num-bytes",
        type=int,
        default=32,
        help="Number of header bytes to read (default: 32)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not print mismatch warnings",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output JSON (after the text output)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output JSON only (no user-readable text)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    results: list[dict] = []
    for path in args.files:
        res = analyze_file(path, num_bytes=args.num_bytes)
        results.append(res)

        if not args.json_only:  # only print text if not JSON-only
            print_user(res, quiet=args.quiet)

    if args.json or args.json_only:
        # Pure data structure, safe for piping to jq, etc.
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
