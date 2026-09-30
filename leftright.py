import re
from pathlib import Path
from tkinter import Tk,filedialog,messagebox
MD_LINK=r"!?\[[^\]]*\]\([^)]*\)"
DELIM=r"(?:\(|\)|\[|\]|\\\{|\\\}|\\langle|\\rangle|\||\.)"
WRAPPED=MD_LINK+r"|\\left\s*"+DELIM+r"|\\right\s*"+DELIM+r"|\\[bB]ig(?:g|l|r)?\s*"+DELIM
BARE=r"(?<!\\)(\(|\)|\[|\])|(\\\{|\\\})|(\\langle|\\rangle)"
PAT=re.compile(WRAPPED+"|"+BARE)
BAR=re.compile(r"(?<!\\)((?:\\\\)*\\?)\|")
WRAPPED_PRE=re.compile(r"(?:\\left|\\right|\\[bB]ig(?:g|l|r)?)\s*$")
def math_spans(text:str):
  spans=[]
  i,n=0,len(text)
  while i<n:
    c=text[i]
    if c=="\\":
      i+=2
      continue
    if c=="$":
      if i+1<n and text[i+1]=="$":
        j=text.find("$$",i+2)
        if j<0:
          break
        spans.append((i,j+2))
        i=j+2
      else:
        j=text.find("$",i+1)
        if j<0:
          break
        spans.append((i,j+1))
        i=j+1
    else:
      i+=1
  return spans
def convert_span(span:str)->str:
  bars=[m for m in BAR.finditer(span) if not WRAPPED_PRE.search(m.string,0,m.start())]
  if len(bars)%2:
    print(f"警告: 数学片段内 | 数量为奇数（无法可靠配对，整段跳过）: {span[:60]!r}")
  else:
    for k in range(len(bars)-1,-1,-1):
      m=bars[k]
      tok=m.group(1)+"|"
      lr="\\left" if k%2==0 else "\\right"
      span=span[:m.start()]+lr+tok+span[m.end():]
  def repl(m):
    s=m.group(0)
    if s in("(", "["):
      return "\\left"+s
    if s in(")", "]"):
      return "\\right"+s
    if s=="\\{":
      return "\\left\\{"
    if s=="\\}":
      return "\\right\\}"
    if s=="\\langle":
      return "\\left\\langle"
    if s=="\\rangle":
      return "\\right\\rangle"
    return s
  return PAT.sub(repl,span)
def convert(text:str)->str:
  out=[]
  pos=0
  for a,b in math_spans(text):
    out.append(text[pos:a])
    out.append(convert_span(text[a:b]))
    pos=b
  out.append(text[pos:])
  return "".join(out)
def process_file(path:Path):
  raw=path.read_bytes()
  bom=raw.startswith(b"\xef\xbb\xbf")
  data=raw[3:] if bom else raw
  try:
    text=data.decode("utf-8")
  except UnicodeDecodeError:
    print(f"跳过（非 UTF-8）: {path}")
    return
  new=convert(text)
  if new==text:
    print(f"无需修改: {path}")
    return
  path.write_bytes((("\ufeff" if bom else "")+new).encode("utf-8"))
  n1=new.count("\\left(")-text.count("\\left(")
  n2=new.count("\\left[")-text.count("\\left[")
  n3=new.count("\\left\\{")-text.count("\\left\\{")
  n4=new.count("\\left|")-text.count("\\left|")
  n5=new.count("\\left\\|")-text.count("\\left\\|")
  n6=new.count("\\left\\langle")-text.count("\\left\\langle")
  n7=new.count("\\right\\rangle")-text.count("\\right\\rangle")
  print(f"已转换: {path}  (+\\left( ×{n1}, +\\left[ ×{n2}, +\\left\\{{ ×{n3}, +\\left| ×{n4}, +\\left\\| ×{n5}, +\\left\\langle ×{n6}, +\\right\\rangle ×{n7})")
def select_and_convert_mds():
  root=Tk()
  root.withdraw()
  pick_files=messagebox.askyesno(
    title="选择处理对象",
    message="请选择要处理的对象类型：\n\n「是」→ 选择 Markdown 文件（可多选）\n「否」→ 选择文件夹（自动处理其中所有 .md）")
  if pick_files:
    selected_files=filedialog.askopenfilenames(title="请选择要转换的 Markdown 文件",filetypes=[("Markdown 文件","*.md"),("All Files","*.*")])
    if not selected_files:
      print("未选择任何文件，退出。")
      return []
    for md_path in selected_files:
      process_file(Path(md_path))
    print(f"转换完成，共处理 {len(selected_files)} 个文件。")
  else:
    folder=filedialog.askdirectory(title="请选择包含 Markdown 文件的文件夹")
    if not folder:
      print("未选择任何文件夹，退出。")
      return []
    md_files=sorted(Path(folder).rglob("*.md"))
    if not md_files:
      print(f"文件夹内未找到任何 .md 文件: {folder}")
      return []
    for md_path in md_files:
      process_file(md_path)
    print(f"转换完成，共处理 {len(md_files)} 个 .md 文件。")
if __name__=="__main__":
  select_and_convert_mds()
