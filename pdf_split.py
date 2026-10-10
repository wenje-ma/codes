import sys
from pathlib import Path
from tkinter import Tk,filedialog,messagebox
import fitz

# GitHub 对单文件有 100MiB(104857600 字节) 硬上限；留出余量，默认按 95MiB 切分，可用 --limit 覆盖
DEFAULT_LIMIT_BYTES=95*1024*1024
def _measure(doc,start:int,end:int,tmp:Path)->int:
  print(f"  测量第{start+1}-{end+1}页…",flush=True)
  out=fitz.open()
  out.insert_pdf(doc,from_page=start,to_page=end)
  out.save(str(tmp),garbage=3,deflate=True)
  out.close()
  size=tmp.stat().st_size
  print(f"    → {size/1048576:.1f}MB",flush=True)
  return size
def _find_end(doc,start:int,n:int,limit_bytes:int,tmp:Path)->int:
  # 用首页大小估算每份大致页数作为二分窗口起点，减少测量次数
  first=_measure(doc,start,start,tmp)
  est=max(1,int(limit_bytes*0.9/max(first,1)))
  guess=min(start+est-1,n-1)
  if guess>start:
    if _measure(doc,start,guess,tmp)<limit_bytes:
      lo,hi=guess,n-1
    else:
      lo,hi=start,guess
  else:
    lo,hi=start,start
  best=start
  while lo<=hi:
    mid=(lo+hi)//2
    if _measure(doc,start,mid,tmp)<limit_bytes:
      best=mid
      lo=mid+1
    else:
      hi=mid-1
  return best
def split_pdf(pdf_path:str,limit_bytes:int=DEFAULT_LIMIT_BYTES,out_dir:Path|None=None)->list[str]:
  pdf_file=Path(pdf_path)
  if not pdf_file.exists():
    raise FileNotFoundError(f"找不到文件: {pdf_file}")
  if pdf_file.stat().st_size<limit_bytes:
    print(f"无需切分: {pdf_file.name}（{pdf_file.stat().st_size/1048576:.1f}MB < 限额 {limit_bytes/1048576:.0f}MB）",flush=True)
    return [str(pdf_file)]
  if out_dir is None:
    out_dir=pdf_file.parent
  out_dir.mkdir(exist_ok=True)
  src=fitz.open(str(pdf_file))
  n=src.page_count
  if n==0:
    src.close()
    raise ValueError(f"空 PDF: {pdf_file.name}")
  tmp=out_dir/f".tmp_{pdf_file.stem}_split.pdf"
  parts=[]
  try:
    start,index=0,1
    while start<n:
      print(f"  确定第{index}份的页数（剩余第{start+1}-{n}页）…",flush=True)
      end=_find_end(src,start,n,limit_bytes,tmp)
      part=out_dir/f"{pdf_file.stem}_part{index}.pdf"
      out=fitz.open()
      out.insert_pdf(src,from_page=start,to_page=end)
      out.save(str(part),garbage=3,deflate=True)
      out.close()
      size=part.stat().st_size
      flag="（⚠️单页已超限额，无法再切小）" if size>=limit_bytes else ""
      print(f"已生成: {part.name}（第{start+1}-{end+1}页，共{end-start+1}页，{size/1048576:.1f}MB）{flag}",flush=True)
      parts.append(str(part))
      start=end+1
      index+=1
  finally:
    src.close()
    if tmp.exists():
      tmp.unlink()
  return parts
def parse_args(argv:list[str]):
  limit=DEFAULT_LIMIT_BYTES
  files=[]
  i=1
  while i<len(argv):
    a=argv[i]
    if a=="--limit" and i+1<len(argv):
      limit=int(float(argv[i+1])*1024*1024)
      i+=2
    else:
      files.append(a)
      i+=1
  return limit,files
def select_pdfs()->list[Path]:
  root=Tk()
  root.withdraw()
  targets:list[Path]=[]
  seen:set[str]=set()
  while True:
    selected_files=filedialog.askopenfilenames(title="请选择要切分的 PDF 文件（可多选；如需跨文件夹请再次选择，取消则结束选择）",filetypes=[("PDF 文件","*.pdf"),("All Files","*.*")])
    if selected_files:
      for f in selected_files:
        p=Path(f)
        if p.suffix.lower()!=".pdf":
          continue
        key=str(p.resolve())
        if key not in seen:
          seen.add(key)
          targets.append(p)
      if not messagebox.askyesno(
        title="继续选择",
        message=f"已选择 {len(targets)} 个 PDF 文件。\n\n「是」→ 继续从其他文件夹选择\n「否」→ 开始切分（每份默认小于 95MB，命令行可用 --limit 覆盖）"):
        break
    else:
      break
  return targets
def main():
  limit,files=parse_args(sys.argv)
  if files:
    selected=[Path(a) for a in files]
  else:
    selected=select_pdfs()
  if not selected:
    print("未选择任何文件，退出。",flush=True)
    return
  done=0
  total=0
  for pdf in selected:
    if not pdf.is_file() or pdf.suffix.lower()!=".pdf":
      print(f"跳过（非 PDF 或不存在）: {pdf}",flush=True)
      continue
    print(f"\n处理: {pdf.name}（{pdf.stat().st_size/1048576:.1f}MB）",flush=True)
    try:
      parts=split_pdf(str(pdf),limit)
      total+=len(parts)
      done+=1
    except Exception as e:
      print(f"失败: {pdf.name}  {str(e)}",flush=True)
  print(f"\n全部完成：共切分 {done} 个文件，生成 {total} 个分卷。",flush=True)
if __name__=="__main__":
  try:
    main()
  finally:
    try:
      sys.stdout.flush()
      input("按回车键退出…")
    except(EOFError,KeyboardInterrupt):
      pass
