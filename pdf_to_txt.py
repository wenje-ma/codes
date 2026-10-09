from pathlib import Path
from tkinter import Tk,filedialog,messagebox
from pypdf import PdfReader
def pdf_to_txt(pdf_path:str,txt_path:str|None=None):
  pdf_file=Path(pdf_path)
  if not pdf_file.exists():
    raise FileNotFoundError(f"找不到文件: {pdf_file}")
  if txt_path is None:
    txt_file=pdf_file.with_suffix(".txt")
  else:
    txt_file=Path(txt_path)
  reader=PdfReader(str(pdf_file))
  pages_text=[]
  for i,page in enumerate(reader.pages,start=1):
    text=page.extract_text() or ""
    pages_text.append(f"--- Page {i} ---\n{text}\n")
  txt_file.write_text("\n".join(pages_text),encoding="utf-8")
  print(f"已生成: {txt_file}")
  return str(txt_file)
def select_and_convert_pdfs():
  root=Tk()
  root.withdraw()
  targets:list[Path]=[]
  seen:set[str]=set()
  while True:
    selected_files=filedialog.askopenfilenames(title='请选择要转换的 PDF 文件（可多选；如需跨文件夹请再次选择，取消则结束选择）',filetypes=[('PDF 文件','*.pdf'),('All Files','*.*')])
    if selected_files:
      for f in selected_files:
        p=Path(f)
        if p.suffix.lower()!='.pdf':
          continue
        key=str(p.resolve())
        if key not in seen:
          seen.add(key)
          targets.append(p)
      if not messagebox.askyesno(
        title='继续选择',
        message=f'已选择 {len(targets)} 个 PDF 文件。\n\n「是」→ 继续从其他文件夹选择\n「否」→ 开始转换'):
        break
    else:
      break
  if not targets:
    print('未选择任何文件，退出。')
    return []
  converted=[]
  for pdf_path in targets:
    output=pdf_to_txt(str(pdf_path))
    converted.append(output)
  print(f'转换完成，共处理 {len(converted)} 个文件。')
  return converted
if __name__=="__main__":
  select_and_convert_pdfs()
