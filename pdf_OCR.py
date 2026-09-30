from pathlib import Path
from tkinter import Tk, filedialog, messagebox
import fitz
from rapidocr_onnxruntime import RapidOCR


def ocr_pdf(pdf_path: str, output_pdf: str | None = None):
  """对扫描版 PDF 做 OCR，输出带可搜索文本层的 PDF。"""
  pdf_file = Path(pdf_path)
  if not pdf_file.exists():
    raise FileNotFoundError(f"找不到文件: {pdf_file}")
  if output_pdf is None:
    out_file = pdf_file.with_name(pdf_file.stem + "_ocr.pdf")
  else:
    out_file = Path(output_pdf)

  doc = fitz.open(str(pdf_file))
  engine = RapidOCR()

  for i, page in enumerate(doc, start=1):
    _add_ocr_text_layer(page, engine)
    print(f"  第{i}页: 已 OCR 并写入文本层")

  doc.save(str(out_file), garbage=3, deflate=True)
  doc.close()
  print(f"已生成: {out_file}")
  return str(out_file)


def _add_ocr_text_layer(page, engine, dpi: int = 200):
  """渲染页面→OCR→写透明文本层。"""
  zoom = dpi / 72
  pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
  result, _ = engine(pix.tobytes("png"))
  if not result:
    return

  font = fitz.Font("china-s")
  tw = fitz.TextWriter(page.rect)

  for box, text, _conf in result:
    text = text.strip()
    if not text:
      continue
    xs = [p[0] / zoom for p in box]
    ys = [p[1] / zoom for p in box]
    x0, y_top = min(xs), min(ys)
    y_bot = max(ys)
    box_h = y_bot - y_top
    fontsize = box_h * 0.85
    if fontsize < 3:
      continue
    baseline = y_bot - box_h * 0.12
    tw.append((x0, baseline), text, font=font, fontsize=fontsize)

  tw.write_text(page, opacity=0)


def select_and_convert_pdfs():
  root = Tk()
  root.withdraw()
  # 先让用户选择目标类型：是单个/多个 PDF 文件，还是整个文件夹
  pick_files = messagebox.askyesno(
    title="选择处理对象",
    message="请选择要处理的对象类型：\n\n「是」→ 选择 PDF 文件（可多选）\n「否」→ 选择文件夹（自动处理其中所有 .pdf）")
  if pick_files:
    selected_files = filedialog.askopenfilenames(
      title='请选择要转换的 PDF 文件',
      filetypes=[('PDF 文件', '*.pdf'), ('All Files', '*.*')]
    )
    if not selected_files:
      print('未选择任何文件，退出。')
      return []
    targets = [Path(f) for f in selected_files]
  else:
    folder = filedialog.askdirectory(title='请选择包含 PDF 文件的文件夹')
    if not folder:
      print('未选择任何文件夹，退出。')
      return []
    targets = sorted(Path(folder).rglob('*.pdf'))
    if not targets:
      print(f'文件夹内未找到任何 .pdf 文件: {folder}')
      return []
  converted = []
  for pdf_path in targets:
    output = ocr_pdf(str(pdf_path))
    converted.append(output)
  print(f'转换完成，共处理 {len(converted)} 个文件。')
  return converted


if __name__ == "__main__":
  select_and_convert_pdfs()
