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
  # 先让用户选择目标类型：是单个/多个 PDF 文件，还是整个文件夹
  pick_files=messagebox.askyesno(
    title="选择处理对象",
    message="请选择要处理的对象类型：\n\n「是」→ 选择 PDF 文件（可多选）\n「否」→ 选择文件夹（自动处理其中所有 .pdf）")
  if pick_files:
    selected_files=filedialog.askopenfilenames(title='请选择要转换的 PDF 文件',filetypes=[('PDF 文件','*.pdf'),('All Files','*.*')])
    if not selected_files:
      print('未选择任何文件，退出。')
      return []
    targets=[Path(f) for f in selected_files]
  else:
    folder=filedialog.askdirectory(title='请选择包含 PDF 文件的文件夹')
    if not folder:
      print('未选择任何文件夹，退出。')
      return []
    targets=sorted(Path(folder).rglob('*.pdf'))
    if not targets:
      print(f'文件夹内未找到任何 .pdf 文件: {folder}')
      return []
  converted=[]
  for pdf_path in targets:
    output=pdf_to_txt(str(pdf_path))
    converted.append(output)
  print(f'转换完成，共处理 {len(converted)} 个文件。')
  return converted
if __name__=="__main__":
  select_and_convert_pdfs()
