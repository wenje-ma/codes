# codes

A small collection of utility scripts for processing Markdown and PDF files. All scripts are Python 3 and open a native multi-select file dialog via `tkinter`. You can pick several files at once, and repeat the dialog as many times as needed to add files from other folders; the scripts then process all of the accumulated files.

## Requirements

### Base

- **Python 3.8+** with **Tkinter**. All scripts use `tkinter` for their file dialogs, so a Python build without Tk support will fail at startup.

### Third-party packages

Install the packages required by the scripts you actually use:

```bash
pip install PyMuPDF                  # for pdf_OCR.py, pdf_split.py
pip install rapidocr-onnxruntime     # for pdf_OCR.py
pip install pypdf                    # for pdf_to_txt.py
```

| Script | Extra packages (pip) | External tools |
| :----: | :------------------: | :------------: |
| `leftright.py` | — | — |
| `md_merge.py` | — | — |
| `pdf_OCR.py` | `PyMuPDF`, `rapidocr-onnxruntime` | — |
| `pdf_split.py` | `PyMuPDF` | — |
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
- **`pdf_split.py`** — Splits a PDF larger than the size limit into consecutive parts, each under the limit, by finding the largest page range that fits. The default limit is **95 MB** (below GitHub's 100 MB hard limit) and can be overridden with `--limit <MB>`. Also accepts PDF paths as command-line arguments.
- **`pdf_to_txt.py`** — Extracts text from PDF pages into a sibling `.txt` file.

## Usage

Run any script from the command line:

```bash
python leftright.py
```

A multi-select file dialog opens (pick several files of the relevant type at
once). After each selection you are asked whether to keep adding files from
other folders:

- **Yes** → the dialog opens again so you can append files from another folder.
- **No** → all accumulated files are processed.

Canceling the file dialog ends the selection: if you already picked files they
are processed, otherwise the script exits without doing anything. Duplicate
selections are skipped automatically.
