# codes

A small collection of utility scripts for processing Markdown and PDF files. All scripts are Python 3 and open a native file dialog via `tkinter` to select either individual files (multi-select supported) or a whole folder — when a folder is chosen, the script recursively processes every matching file in it.

## Requirements

### Base

- **Python 3.8+** with **Tkinter**. All scripts use `tkinter` for their file dialogs, so a Python build without Tk support will fail at startup.

### Third-party packages

Install the packages required by the scripts you actually use:

```bash
pip install PyMuPDF                  # for pdf_OCR.py
pip install rapidocr-onnxruntime     # for pdf_OCR.py
pip install pypdf                    # for pdf_to_txt.py
```

| Script | Extra packages (pip) | External tools |
| :----: | :------------------: | :------------: |
| `leftright.py` | — | — |
| `md_merge.py` | — | — |
| `pdf_OCR.py` | `PyMuPDF`, `rapidocr-onnxruntime` | — |
| `pdf_to_txt.py` | `pypdf` | — |
| `pdf_to_svg.py` | — | `pdf2svg` (see below) |
| `md_to_pdf.exe` | — | — |

### External tools

- **`pdf_to_svg.py`** requires the `pdf2svg` command-line tool. The script looks for it in `C:\rtools45\mingw64\bin\pdf2svg.exe`, falling back to whatever `pdf2svg` is on your `PATH`. Install it and make sure it is discoverable before running this script.

## Scripts

- **`leftright.py`** — Adds `\left` / `\right` to bare brackets, braces and pipes inside `$...$` / `$$...$$` math spans of Markdown files.
- **`md_merge.py`** — Concatenates selected Markdown files into a single `document.md`, which is in the same directory as the first file.
- **`pdf_OCR.py`** — OCRs scanned PDFs and writes a searchable text layer back into an `_ocr.pdf` copy.
- **`pdf_to_svg.py`** — Converts each page of a PDF into SVG files using `pdf2svg`. Also accepts PDF paths as command-line arguments instead of the dialog.
- **`pdf_to_txt.py`** — Extracts text from PDF pages into a sibling `.txt` file.

## Usage

Run any script from the command line:

```bash
python leftright.py
```

A dialog first asks whether you want to pick **files** or a **folder**:

- **Yes** → choose one or more files of the relevant type.
- **No** → choose a folder; all matching files under it (including
  subfolders) are processed automatically.
