import re
import shutil
import subprocess
import sys
from pathlib import Path
from tkinter import Tk,filedialog

PDF2SVG_CANDIDATES=[Path(r"C:\rtools45\mingw64\bin\pdf2svg.exe")]
def find_pdf2svg():
  for p in PDF2SVG_CANDIDATES:
    if p.is_file():
      return p
  found=shutil.which("pdf2svg")
  return Path(found) if found else None
def convert_pdf(pdf2svg,pdf:Path)->str:
  base=pdf.stem
  out_dir=pdf.parent
  target=out_dir/f"{base}.svg"
  if target.is_file() and target.stat().st_mtime>=pdf.stat().st_mtime:
    return f"无需修改: {target.name}（已存在且最新）"
  tmp_dir=out_dir/".tmp_pdf2svg"
  tmp_dir.mkdir(exist_ok=True)
  try:
    template=tmp_dir/f"{base}_%d.svg"
    proc=subprocess.run([str(pdf2svg),str(pdf),str(template),"all"],capture_output=True,text=True,encoding="utf-8",errors="replace")
    if proc.returncode!=0:
      err=(proc.stderr or proc.stdout or "").strip()
      return f"失败: {pdf.name}  exit={proc.returncode}  {err[:200]}"
    def page_no(p):
      return int(re.search(r"_(\d+)\.svg$",p.name).group(1))
    outputs=sorted(tmp_dir.glob(f"{base}_*.svg"),key=page_no)
    if not outputs:
      return f"失败: {pdf.name}（pdf2svg 未产出任何 SVG）"
    if len(outputs)==1:
      outputs[0].replace(target)
      return f"已转换: {target.name}（单页）"
    names=[]
    for p in outputs:
      dest=out_dir/p.name
      p.replace(dest)
      names.append(dest.name)
    return f"已转换: {pdf.name} → {len(outputs)} 页（"+", ".join(names)+"，md 请引用带页码的文件）"
  finally:
    if tmp_dir.is_dir():
      for leftover in tmp_dir.iterdir():
        leftover.unlink()
      tmp_dir.rmdir()
def main():
  pdf2svg=find_pdf2svg()
  if pdf2svg is None:
    print("未找到 pdf2svg.exe。请先安装后再运行。")
    return
  if len(sys.argv)>1:
    selected=[Path(a) for a in sys.argv[1:]]
  else:
    script_dir=Path(__file__).resolve().parent
    figures=script_dir/"figures"
    root=Tk()
    root.withdraw()
    files=filedialog.askopenfilenames(title="请选择要转换为 SVG 的 PDF 文件",initialdir=str(figures if figures.is_dir() else script_dir),filetypes=[("PDF 文件","*.pdf"),("All Files","*.*")])
    if not files:
      print("未选择任何文件，退出。")
      return
    selected=[Path(f) for f in files]
  print(f"使用: {pdf2svg}")
  done=0
  for pdf in selected:
    if not pdf.is_file() or pdf.suffix.lower()!=".pdf":
      print(f"跳过（非 PDF 或不存在）: {pdf}")
      continue
    print(convert_pdf(pdf2svg,pdf))
    done+=1
  print(f"转换完成，共处理 {done} 个文件。")
if __name__=="__main__":
  try:
    main()
  finally:
    try:
      input("按回车键退出…")
    except(EOFError,KeyboardInterrupt):
      pass
