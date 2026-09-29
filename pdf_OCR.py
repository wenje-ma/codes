import re
from pathlib import Path
from tkinter import Tk, filedialog
import fitz
from rapidocr_onnxruntime import RapidOCR


# ---------- 标题识别规则 ----------
# 按优先级匹配，命中即返回层级（1=一级，2=二级，3=三级）
_HEADING_PATTERNS = [
  (re.compile(r"^\s*第\s*[一二三四五六七八九十百零\d]+\s*[篇章节部分]"), 1),
  (re.compile(r"^\s*附\s*录\s*[A-Z一二三四五六七八九十\d]*"), 1),
  (re.compile(r"^\s*[一二三四五六七八九十]+\s*[、.．]"), 2),
  (re.compile(r"^\s*（[一二三四五六七八九十]+）"), 3),
  (re.compile(r"^\s*\d+\s*[、.．]\s*\S"), 2),
  (re.compile(r"^\s*\d+\.\d+(\.\d+)*\s*\S"), 3),
]


def ocr_pdf(pdf_path: str, output_pdf: str | None = None, make_toc: bool = False):
  """对扫描版 PDF 做 OCR，输出带可搜索文本层（可选自动书签）的 PDF。"""
  pdf_file = Path(pdf_path)
  if not pdf_file.exists():
    raise FileNotFoundError(f"找不到文件: {pdf_file}")
  if output_pdf is None:
    out_file = pdf_file.with_name(pdf_file.stem + "_ocr.pdf")
  else:
    out_file = Path(output_pdf)

  doc = fitz.open(str(pdf_file))
  engine = RapidOCR()

  # 收集所有行：(page_no, y, fontsize, text, x0)
  all_lines = []
  for i, page in enumerate(doc, start=1):
    lines = _add_ocr_text_layer(page, engine)
    for y, fs, text, x0 in lines:
      all_lines.append((i, y, fs, text, x0))
    print(f"  第{i}页: 已 OCR 并写入文本层")

  if make_toc and all_lines:
    toc = _build_toc(all_lines)
    if toc:
      doc.set_toc(toc)
      print(f"  已生成 {len(toc)} 条书签")
    else:
      print("  未识别到明显标题，跳过书签生成")

  doc.save(str(out_file), garbage=3, deflate=True)
  doc.close()
  print(f"已生成: {out_file}")
  return str(out_file)


def _add_ocr_text_layer(page, engine, dpi: int = 200):
  """渲染页面→OCR→写透明文本层，返回该页 [(y, fontsize, text, x0), ...]。"""
  zoom = dpi / 72
  pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
  result, _ = engine(pix.tobytes("png"))
  if not result:
    return []

  font = fitz.Font("china-s")
  tw = fitz.TextWriter(page.rect)
  out = []

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
    out.append((y_top, fontsize, text, x0))

  tw.write_text(page, opacity=0)
  return out


def _build_toc(lines):
  """根据字号分布 + 正则规则，把候选行整理成 PyMuPDF 的 toc 列表。"""
  # 1) 字号统计：用中位数作为正文字号基准
  sizes = sorted(fs for _, _, fs, _, _ in lines)
  median = sizes[len(sizes) // 2]

  # 2) 逐行判定
  toc = []
  for page_no, y, fs, text, x0 in lines:
    level = _detect_heading_level(text, fs, median)
    if level is None:
      continue
    title = text.strip()
    if len(title) > 80:  # 过长更像正文段落
      continue
    toc.append([level, title, page_no])

  # 3) 简单去重（同页同标题文字重复）
  seen = set()
  cleaned = []
  for item in toc:
    key = (item[2], item[1])
    if key in seen:
      continue
    seen.add(key)
    cleaned.append(item)
  return cleaned


def _detect_heading_level(text: str, fontsize: float, median: float):
  """返回 1/2/3，非标题返回 None。"""
  # 正则优先
  for pat, level in _HEADING_PATTERNS:
    if pat.match(text):
      return level
  # 字号辅助：明显大于正文的行视为标题
  if fontsize >= median * 1.45:
    return 1
  if fontsize >= median * 1.25:
    return 2
  return None


def select_and_convert_pdfs():
  root = Tk()
  root.withdraw()
  selected_files = filedialog.askopenfilenames(
    title='请选择要转换的 PDF 文件',
    filetypes=[('PDF 文件', '*.pdf'), ('All Files', '*.*')]
  )
  if not selected_files:
    print('未选择任何文件，退出。')
    return []
  converted = []
  for pdf_path in selected_files:
    output = ocr_pdf(pdf_path)
    converted.append(output)
  print(f'转换完成，共处理 {len(converted)} 个文件。')
  return converted


if __name__ == "__main__":
  select_and_convert_pdfs()
