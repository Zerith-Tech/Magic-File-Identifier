# Magic-File-Identifier
A Python-based file type identification tool that analyzes **magic numbers** (file headers) to determine a file’s *true type*, compares it with the file extension, and flags mismatches.

Designed for **digital forensics, malware analysis, and security automation**.

---

## Features

- 🔍 **Magic Number Analysis**
  - Reads raw file headers (binary)
  - Identifies file type using known magic byte signatures

- ⚠️ **Mismatch Detection**
  - Compares detected file type vs file extension
  - Highlights suspicious or disguised files

- 🧠 **Contextual Validation**
  - Integrates system `file` command for cross-verification

- 🎨 **User-Friendly Output**
  - Colored, structured terminal output

- 🤖 **Automation-Ready**
  - JSON output for scripting, pipelines, and tooling
  - JSON-only mode for clean piping

- 🧩 **Flexible CLI**
  - Analyze one or many files
  - Configurable header length
  - Quiet mode for clean logs

---

## Why This Tool Exists

Attackers frequently **disguise files** by changing their extensions
(e.g. `payload.exe` → `image.jpg`).  
Relying on file extensions alone is unsafe.

This tool:
- Reads what the file *is*, not what it *claims to be*
- Helps identify hidden executables, malformed files, and suspicious artifacts
- Demonstrates how magic number detection works at a low level

---

## Requirements

- Python **3.10+**
- Unix-like system for `file` command (Linux / macOS / WSL)
  - On Windows, `file` output will be unavailable unless using WSL

No external Python libraries required.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/magic-file-identifier.git
cd magic-file-identifier
```
---
## Usage
Basic Analysis (Colored Output)
```bash
python3 magic_file_id.py suspicious.jpg
```
Analyze Multiple Files
```bash
python3 magic_file_id.py file1.bin file2.pdf file3.png
```
Increase Header Size
```bash
python3 magic_file_id.py -n 64 largefile.bin
```
Suppress Mismatch Warnings
```bash
python3 magic_file_id.py --quiet file.bin
```

---

## Output Modes
Text + JSON

Useful for logging or mixed user / machine use.
```bash
python3 magic_file_id.py suspicious.jpg --json
```
JSON Only (Automation / Piping)

Perfect for CI pipelines, scripts, and parsing tools like jq.
```bash
python3 magic_file_id.py suspicious.jpg --json-only | jq
```

Example JSON output:
```bash
[
  {
    "path": "suspicious.jpg",
    "exists": true,
    "error": null,
    "magic": {
      "raw_hex": "89504e470d0a1a0a...",
      "detected_type": "PNG image"
    },
    "other": {
      "extension": ".jpg",
      "file_output": "PNG image data, 800 x 600, 8-bit colormap"
    },
    "mismatch": true
  }
]
```

---

## Help

View full CLI help with examples:
```bash
python magic_file_id.py --help
```

## Supported File Types (Partial)
- Images: PNG, JPEG, GIF, BMP, TIFF
- Archives: ZIP, GZIP, BZIP2, RAR, 7-Zip, TAR
- Executables: ELF, PE (EXE / DLL)
- Documents & Media: PDF, MP3, MP4

(Planning to expand via magic number database.)

---

## Educational Note
- This project was built to deepen understanding of:
- File formats and headers
- Binary analysis
- Digital forensics fundamentals
- Security tooling design
